"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { CheckCircle2, LogOut } from "lucide-react";
import { useTranslations } from "next-intl";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/features/auth/auth-provider";
import { FormAlert, PasswordField, SubmitButton } from "@/features/auth/fields";
import { useRouter } from "@/i18n/navigation";
import { changePassword } from "@/services/me";
import { CabinetHeader } from "./cabinet-shell";

const schema = z
  .object({
    current: z.string().min(1, "required"),
    next: z
      .string()
      .min(8, "passwordMin")
      .max(128, "passwordMax")
      .regex(/\p{L}/u, "passwordWeak")
      .regex(/\d/, "passwordWeak"),
    confirm: z.string().min(1, "required"),
  })
  .refine((d) => d.next === d.confirm, { path: ["confirm"], message: "passwordMismatch" });
type Values = z.infer<typeof schema>;

export function SettingsView() {
  const t = useTranslations("cabinet");
  const { logout } = useAuth();
  const router = useRouter();
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<Values>({ resolver: zodResolver(schema), defaultValues: { current: "", next: "", confirm: "" } });

  const onSubmit = handleSubmit(async ({ current, next }) => {
    setDone(false);
    setError(null);
    const result = await changePassword(current, next);
    if (result === "ok") {
      reset();
      setDone(true);
    } else {
      setError(t(result));
    }
  });

  return (
    <>
      <CabinetHeader title={t("settingsTitle")} />
      <div className="flex flex-col gap-6">
        <section aria-labelledby="pwd" className="rounded-2xl border border-border bg-card p-6">
          <h2 id="pwd" className="mb-5 text-lg font-bold">
            {t("passwordTitle")}
          </h2>
          <form noValidate onSubmit={onSubmit} className="flex max-w-md flex-col gap-5">
            <FormAlert message={error} />
            {done && (
              <p role="status" className="inline-flex items-center gap-1.5 text-sm text-success">
                <CheckCircle2 className="size-4" aria-hidden="true" />
                {t("passwordChanged")}
              </p>
            )}
            <PasswordField
              id="pwd-current"
              label={t("currentPassword")}
              autoComplete="current-password"
              error={errors.current?.message}
              {...register("current")}
            />
            <PasswordField
              id="pwd-new"
              label={t("newPassword")}
              autoComplete="new-password"
              error={errors.next?.message}
              {...register("next")}
            />
            <PasswordField
              id="pwd-confirm"
              label={t("confirmPassword")}
              autoComplete="new-password"
              error={errors.confirm?.message}
              {...register("confirm")}
            />
            <SubmitButton pending={isSubmitting} label={t("changePassword")} />
          </form>
        </section>

        <section aria-labelledby="session" className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-border bg-card p-6">
          <div>
            <h2 id="session" className="text-lg font-bold">
              {t("sessionTitle")}
            </h2>
            <p className="text-sm text-muted-foreground">{t("sessionText")}</p>
          </div>
          <Button
            variant="outline"
            onClick={async () => {
              await logout();
              router.replace("/");
              router.refresh();
            }}
          >
            <LogOut aria-hidden="true" />
            {t("logout")}
          </Button>
        </section>
      </div>
    </>
  );
}
