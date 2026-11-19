import { ApiError, apiFetch } from "@/lib/api";
import type { CurrentUser } from "@/types/user";

export type AuthFailure =
  | "invalidCredentials"
  | "emailTaken"
  | "weakPassword"
  | "tooManyRequests"
  | "accountDisabled"
  | "network"
  | "unknown";

export type AuthResult = { ok: true; user: CurrentUser } | { ok: false; reason: AuthFailure };

function toFailure(error: unknown): AuthFailure {
  if (error instanceof ApiError) {
    if (error.status === 401) return "invalidCredentials";
    if (error.status === 403) return "accountDisabled";
    if (error.status === 409) return "emailTaken";
    if (error.status === 422) return "weakPassword";
    if (error.status === 429) return "tooManyRequests";
    return "unknown";
  }
  return "network";
}

async function call(path: string, body: unknown): Promise<AuthResult> {
  try {
    // The backend sets the HttpOnly session cookie on success.
    const user = await apiFetch<CurrentUser>(path, { method: "POST", body, timeoutMs: 10_000 });
    return { ok: true, user };
  } catch (error) {
    return { ok: false, reason: toFailure(error) };
  }
}

export function loginWithEmail(email: string, password: string): Promise<AuthResult> {
  return call("/auth/login", { email, password });
}

export function registerWithEmail(
  fullName: string,
  email: string,
  password: string,
): Promise<AuthResult> {
  return call("/auth/register", { full_name: fullName, email, password });
}

export async function fetchCurrentUser(): Promise<CurrentUser | null> {
  try {
    return await apiFetch<CurrentUser>("/users/me", { cache: "no-store" });
  } catch {
    return null;
  }
}

export async function logout(): Promise<void> {
  await apiFetch("/auth/logout", { method: "POST" }).catch(() => undefined);
}
