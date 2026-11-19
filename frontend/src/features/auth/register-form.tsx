"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslations } from "next-intl";
import { useForm } from "react-hook-form";
import { FieldError } from "@/components/ui/form-controls";
import { Link } from "@/i18n/navigation";
import { registerWithEmail } from "@/services/auth";
import { FormAlert, PasswordField, SubmitButton, TextField } from "./fields";
import { isErrorKey, type RegisterValues, registerSchema } from "./schemas";
import { useAuthSubmit } from "./use-auth-submit";

const legalLink = "font-medium text-accent underline-offset-4 hover:underline";

export function RegisterForm() {
  const t = useTranslations("auth");
  const { serverError, handle } = useAuthSubmit();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<RegisterValues>({
    resolver: zodResolver(registerSchema),
    defaultValues: { fullName: "", email: "", password: "", confirmPassword: "", acceptTerms: false },
    mode: "onTouched",
  });

  const onSubmit = handleSubmit(({ fullName, email, password }) =>
    handle(registerWithEmail(fullName, email, password)),
  );

  const termsError = errors.acceptTerms?.message;

  return (
    <form noValidate onSubmit={onSubmit} className="flex flex-col gap-5">
      <FormAlert message={serverError} />
      <TextField
        id="reg-name"
        label={t("fullName")}
        autoComplete="name"
        error={errors.fullName?.message}
        {...register("fullName")}
      />
      <TextField
        id="reg-email"
        label={t("email")}
        type="email"
        autoComplete="email"
        inputMode="email"
        error={errors.email?.message}
        {...register("email")}
      />
      <PasswordField
        id="reg-password"
        label={t("password")}
        autoComplete="new-password"
        hint={t("passwordHint")}
        error={errors.password?.message}
        {...register("password")}
      />
      <PasswordField
        id="reg-confirm"
        label={t("confirmPassword")}
        autoComplete="new-password"
        error={errors.confirmPassword?.message}
        {...register("confirmPassword")}
      />
      <div className="flex flex-col gap-1.5">
        <label className="flex items-start gap-3 text-sm">
          <input
            type="checkbox"
            className="mt-0.5 size-4 shrink-0 accent-[#7856FF]"
            aria-invalid={termsError ? true : undefined}
            aria-labelledby="reg-terms-label"
            aria-describedby={termsError ? "reg-terms-error" : undefined}
            {...register("acceptTerms")}
          />
          <span id="reg-terms-label" className="text-muted-foreground">
            {t.rich("acceptTerms", {
              terms: (chunks) => (
                <Link href="/terms" target="_blank" className={legalLink}>
                  {chunks}
                </Link>
              ),
              privacy: (chunks) => (
                <Link href="/privacy" target="_blank" className={legalLink}>
                  {chunks}
                </Link>
              ),
            })}
          </span>
        </label>
        <FieldError
          id="reg-terms-error"
          message={isErrorKey(termsError) ? t(`errors.${termsError}`) : undefined}
        />
      </div>
      <SubmitButton pending={isSubmitting} label={t("submitRegister")} />
    </form>
  );
}
