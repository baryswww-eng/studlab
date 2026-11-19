/** Response of GET /api/v1/health */
export interface HealthResponse {
  status: "ok";
  service: string;
  version: string;
  environment: string;
}

/** Response of GET /api/v1/health/db */
export interface DatabaseHealthResponse {
  status: "ok" | "unavailable";
  database: string;
  latency_ms: number | null;
}

/** Standard error body produced by the backend. */
export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
  };
}
