"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useTranslations } from "next-intl";
import { useForm } from "react-hook-form";
import { loginWithEmail } from "@/services/auth";
import { FormAlert, PasswordField, SubmitButton, TextField } from "./fields";
import { type LoginValues, loginSchema } from "./schemas";
import { useAuthSubmit } from "./use-auth-submit";

export function LoginForm() {
  const t = useTranslations("auth");
  const { serverError, handle } = useAuthSubmit();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: "", password: "" },
    mode: "onTouched",
  });

  const onSubmit = handleSubmit(({ email, password }) => handle(loginWithEmail(email, password)));

  return (
    <form noValidate onSubmit={onSubmit} className="flex flex-col gap-5">
      <FormAlert message={serverError} />
      <TextField
        id="login-email"
        label={t("email")}
        type="email"
        autoComplete="email"
        inputMode="email"
        error={errors.email?.message}
        {...register("email")}
      />
      <PasswordField
        id="login-password"
        label={t("password")}
        autoComplete="current-password"
        error={errors.password?.message}
        {...register("password")}
      />
      <SubmitButton pending={isSubmitting} label={t("submitLogin")} />
    </form>
  );
}
