"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { CheckCircle2 } from "lucide-react";
import { useFormatter, useTranslations } from "next-intl";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Badge } from "@/components/ui/badge";
import { Input, Label } from "@/components/ui/form-controls";
import { useAuth } from "@/features/auth/auth-provider";
import { FormAlert, SubmitButton, TextField } from "@/features/auth/fields";
import { updateProfile } from "@/services/me";
import { CabinetHeader } from "./cabinet-shell";

const schema = z.object({ fullName: z.string().trim().min(2, "nameMin").max(120, "nameMax") });
type Values = z.infer<typeof schema>;

export function ProfileView() {
  const t = useTranslations("cabinet");
  const format = useFormatter();
  const { user, setUser } = useAuth();
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting, isDirty },
    reset,
  } = useForm<Values>({ resolver: zodResolver(schema), defaultValues: { fullName: user?.full_name ?? "" } });

  if (!user) return null;

  const onSubmit = handleSubmit(async ({ fullName }) => {
    setSaved(false);
    setError(null);
    try {
      const updated = await updateProfile(fullName);
      setUser(updated);
      reset({ fullName: updated.full_name });
      setSaved(true);
    } catch {
      setError(t("unknownError"));
    }
  });

  return (
    <>
      <CabinetHeader title={t("profileTitle")} text={t("profileText")} />
      <div className="flex flex-col gap-6 rounded-2xl border border-border bg-card p-6">
        <div className="flex items-center gap-4">
          <span
            aria-hidden="true"
            className="flex size-16 items-center justify-center rounded-full bg-gradient-to-br from-primary to-accent text-2xl font-bold text-white"
          >
            {user.full_name.charAt(0).toUpperCase()}
          </span>
          <div>
            <p className="text-lg font-semibold">{user.full_name}</p>
            <div className="mt-1 flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
              <Badge variant="primary">{t(`roles.${user.role}`)}</Badge>
              <span>{t("memberSince", { date: format.dateTime(new Date(user.created_at), { dateStyle: "long" }) })}</span>
            </div>
          </div>
        </div>

        <form noValidate onSubmit={onSubmit} className="flex max-w-md flex-col gap-5">
          <FormAlert message={error} />
          <TextField
            id="profile-name"
            label={t("fullName")}
            autoComplete="name"
            error={errors.fullName?.message}
            {...register("fullName", { onChange: () => setSaved(false) })}
          />
          <div className="flex flex-col gap-1.5">
            <Label htmlFor="profile-email">{t("email")}</Label>
            <Input id="profile-email" value={user.email} readOnly aria-describedby="profile-email-hint" className="opacity-70" />
            <p id="profile-email-hint" className="text-xs text-muted-foreground">
              {t("emailHint")}
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-4">
            <div className="w-40">
              <SubmitButton pending={isSubmitting} label={t("save")} />
            </div>
            {saved && !isDirty && (
              <p role="status" className="inline-flex items-center gap-1.5 text-sm text-success">
                <CheckCircle2 className="size-4" aria-hidden="true" />
                {t("saved")}
              </p>
            )}
          </div>
        </form>
      </div>
    </>
  );
}
