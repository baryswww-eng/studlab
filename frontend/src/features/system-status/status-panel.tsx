import { AlertTriangle, CheckCircle2, XCircle } from "lucide-react";
import { getFormatter, getTranslations } from "next-intl/server";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { getSystemStatus } from "@/services/health";
import { RefreshButton } from "./refresh-button";

function StatusRow({
  label,
  ok,
  okText,
  downText,
  details,
}: {
  label: string;
  ok: boolean;
  okText: string;
  downText: string;
  details: string[];
}) {
  const Icon = ok ? CheckCircle2 : XCircle;
  return (
    <li className="flex items-start justify-between gap-4 rounded-xl border border-border bg-background/40 p-4">
      <div className="min-w-0">
        <p className="font-medium">{label}</p>
        {details.length > 0 && (
          <p className="mt-0.5 text-xs text-muted-foreground">{details.join(" · ")}</p>
        )}
      </div>
      <span
        className={cn(
          "inline-flex shrink-0 items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold",
          ok ? "bg-success/15 text-success" : "bg-destructive/15 text-destructive",
        )}
      >
        <Icon className="size-3.5" aria-hidden="true" />
        {ok ? okText : downText}
      </span>
    </li>
  );
}

export async function StatusPanel() {
  const [t, format, status] = await Promise.all([
    getTranslations("status"),
    getFormatter(),
    getSystemStatus(),
  ]);
  const { api, database } = status;
  const dbOk = database.ok && database.data.status === "ok";

  const apiDetails = api.ok
    ? [
        t("version", { version: api.data.version }),
        t("environment", { env: api.data.environment }),
        t("latency", { ms: api.latencyMs }),
      ]
    : [];
  const dbDetails =
    database.ok && database.data.latency_ms !== null
      ? [t("latency", { ms: Math.round(database.data.latency_ms) })]
      : [];

  const problem = !api.ok ? t("apiUnreachable") : !dbOk ? t("dbUnreachable") : null;

  return (
    <Card>
      <CardHeader className="flex-row items-start justify-between gap-4 space-y-0">
        <div className="flex flex-col gap-1.5">
          <CardTitle>{t("title")}</CardTitle>
          <CardDescription>{t("description")}</CardDescription>
        </div>
        <RefreshButton label={t("refresh")} />
      </CardHeader>
      <CardContent className="flex flex-col gap-4">
        <ul className="flex flex-col gap-3" aria-live="polite">
          <StatusRow label={t("frontend")} ok okText={t("ok")} downText={t("down")} details={[]} />
          <StatusRow
            label={t("api")}
            ok={api.ok}
            okText={t("ok")}
            downText={t("down")}
            details={apiDetails}
          />
          <StatusRow
            label={t("database")}
            ok={dbOk}
            okText={t("ok")}
            downText={t("down")}
            details={dbDetails}
          />
        </ul>
        {problem && (
          <p
            role="alert"
            className="flex items-start gap-2 rounded-xl border border-warning/40 bg-warning/10 p-3 text-sm text-warning"
          >
            <AlertTriangle className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
            {problem}
          </p>
        )}
        <p className="text-xs text-muted-foreground">
          {t("checkedAt", {
            time: format.dateTime(status.checkedAt, { timeStyle: "medium", dateStyle: "short" }),
          })}
        </p>
      </CardContent>
    </Card>
  );
}
