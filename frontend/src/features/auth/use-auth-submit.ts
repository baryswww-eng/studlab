"use client";

import { useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { useState } from "react";
import { useRouter } from "@/i18n/navigation";
import type { AuthResult } from "@/services/auth";
import { useAuth } from "./auth-provider";
import { safeNextPath } from "./safe-redirect";

/** Runs an auth action, shows a translated error or signs in and redirects to ?next=. */
export function useAuthSubmit() {
  const t = useTranslations("auth.errors");
  const router = useRouter();
  const params = useSearchParams();
  const { setUser } = useAuth();
  const [serverError, setServerError] = useState<string | null>(null);

  async function handle(result: Promise<AuthResult>) {
    setServerError(null);
    const r = await result;
    if (!r.ok) {
      setServerError(t(r.reason));
      return;
    }
    setUser(r.user);
    router.replace(safeNextPath(params.get("next")));
    router.refresh();
  }

  return { serverError, handle };
}
