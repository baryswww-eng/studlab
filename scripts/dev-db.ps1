<#
  Local PostgreSQL for development, without Docker or a system-wide install.
  Binaries live in .local/pg (pip package "pgserver"), data in .local/pgdata.

  Usage:
    powershell -ExecutionPolicy Bypass -File scripts/dev-db.ps1 start
    powershell -ExecutionPolicy Bypass -File scripts/dev-db.ps1 stop
    powershell -ExecutionPolicy Bypass -File scripts/dev-db.ps1 status
#>
param([ValidateSet("start", "stop", "status")][string]$Command = "start")

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$bin = Join-Path $root ".local\pg\pgserver\pginstall\bin"
$data = Join-Path $root ".local\pgdata"
$log = Join-Path $root ".local\postgres.log"
$port = 5432

if (-not (Test-Path (Join-Path $bin "pg_ctl.exe"))) {
    Write-Host "PostgreSQL binaries not found. Installing into .local/pg ..."
    & (Join-Path $root "backend\.venv\Scripts\python.exe") -m pip install -q --target (Join-Path $root ".local\pg") pgserver==0.1.4 --no-deps
}

# Read POSTGRES_* values from the root .env file.
$envFile = Join-Path $root ".env"
if (-not (Test-Path $envFile)) { throw ".env not found. Run: Copy-Item .env.example .env" }
$cfg = @{}
foreach ($line in Get-Content $envFile) {
    if ($line -match '^\s*([A-Z_][A-Z0-9_]*)\s*=\s*(.*)\s*$') { $cfg[$Matches[1]] = $Matches[2] }
}
$user = if ($cfg.POSTGRES_USER) { $cfg.POSTGRES_USER } else { "studlab" }
$db = if ($cfg.POSTGRES_DB) { $cfg.POSTGRES_DB } else { "studlab" }
$password = $cfg.POSTGRES_PASSWORD
if (-not $password) { throw "POSTGRES_PASSWORD is empty in .env" }

$pgCtl = Join-Path $bin "pg_ctl.exe"

switch ($Command) {
    "status" { & $pgCtl -D $data status; exit $LASTEXITCODE }
    "stop" { & $pgCtl -D $data -m fast -w stop; exit $LASTEXITCODE }
    "start" {
        if (-not (Test-Path (Join-Path $data "PG_VERSION"))) {
            Write-Host "Initializing cluster in .local/pgdata ..."
            $pwFile = New-TemporaryFile
            try {
                [IO.File]::WriteAllText($pwFile.FullName, $password)
                & (Join-Path $bin "initdb.exe") -D $data -U $user "--pwfile=$($pwFile.FullName)" `
                    -A scram-sha-256 -E UTF8 --locale=C | Out-Null
                if ($LASTEXITCODE -ne 0) { throw "initdb failed" }
            } finally { Remove-Item $pwFile.FullName -Force }
        }

        & $pgCtl -D $data status *> $null
        if ($LASTEXITCODE -ne 0) {
            # Listen on localhost only.
            & $pgCtl -D $data -l $log -o "-p $port -h 127.0.0.1" -w start
            if ($LASTEXITCODE -ne 0) { throw "PostgreSQL failed to start, see .local/postgres.log" }
        }

        $env:PGPASSWORD = $password
        $psql = Join-Path $bin "psql.exe"
        foreach ($name in @($db, "${db}_test")) {
            $exists = & $psql -h 127.0.0.1 -p $port -U $user -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='$name'"
            if ($exists -ne "1") {
                & (Join-Path $bin "createdb.exe") -h 127.0.0.1 -p $port -U $user $name
                Write-Host "Created database $name"
            }
        }
        Remove-Item Env:PGPASSWORD
        Write-Host "PostgreSQL is running on 127.0.0.1:$port (databases: $db, ${db}_test)"
    }
}
