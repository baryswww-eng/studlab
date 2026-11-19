import { apiFetch } from "@/lib/api";
import type { DatabaseHealthResponse, HealthResponse } from "@/types/api";

export type ServiceCheck<T> =
  | { ok: true; data: T; latencyMs: number }
  | { ok: false; latencyMs: number };

async function timed<T>(fn: () => Promise<T>): Promise<ServiceCheck<T>> {
  const start = performance.now();
  try {
    const data = await fn();
    return { ok: true, data, latencyMs: Math.round(performance.now() - start) };
  } catch {
    return { ok: false, latencyMs: Math.round(performance.now() - start) };
  }
}

export interface SystemStatus {
  api: ServiceCheck<HealthResponse>;
  database: ServiceCheck<DatabaseHealthResponse>;
  checkedAt: Date;
}

/** Checks the backend and its database connection. Never throws. */
export async function getSystemStatus(): Promise<SystemStatus> {
  const [api, database] = await Promise.all([
    timed(() => apiFetch<HealthResponse>("/health", { cache: "no-store", timeoutMs: 3000 })),
    timed(() =>
      apiFetch<DatabaseHealthResponse>("/health/db", { cache: "no-store", timeoutMs: 4000 }),
    ),
  ]);
  return { api, database, checkedAt: new Date() };
}
