import type { ApiErrorBody } from "@/types/api";

/**
 * Base URL of the FastAPI backend.
 * - On the server (SSR) we call the backend directly: API_INTERNAL_URL.
 * - In the browser we call the site's own /api/v1 proxy (same origin → first-party
 *   cookies, no CORS) unless NEXT_PUBLIC_API_URL points somewhere explicitly.
 */
export function apiBaseUrl(): string {
  const isServer = typeof window === "undefined";
  const url = isServer
    ? (process.env.API_INTERNAL_URL ?? "http://localhost:8000")
    : (process.env.NEXT_PUBLIC_API_URL ?? "");
  return url.replace(/\/$/, "");
}

export class ApiError extends Error {
  constructor(
    public readonly status: number,
    public readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

type RequestOptions = Omit<RequestInit, "body"> & {
  body?: unknown;
  timeoutMs?: number;
};

/** Typed JSON request to /api/v1/*. Throws ApiError on non-2xx responses. */
export async function apiFetch<T>(
  path: string,
  { body, timeoutMs = 5000, headers, ...init }: RequestOptions = {},
): Promise<T> {
  const response = await fetch(`${apiBaseUrl()}/api/v1${path}`, {
    ...init,
    credentials: "include",
    headers: {
      Accept: "application/json",
      ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
      ...headers,
    },
    body: body !== undefined ? JSON.stringify(body) : undefined,
    signal: init.signal ?? AbortSignal.timeout(timeoutMs),
  });

  const data: unknown = await response.json().catch(() => null);

  if (!response.ok) {
    const err = (data as ApiErrorBody | null)?.error;
    throw new ApiError(
      response.status,
      err?.code ?? "http_error",
      err?.message ?? response.statusText,
    );
  }
  return data as T;
}
