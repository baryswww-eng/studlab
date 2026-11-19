"use client";

import { AlertCircle, Eye, EyeOff, Loader2 } from "lucide-react";
import { useTranslations } from "next-intl";
import { type ComponentProps, type ReactNode, useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { FieldError, Input, Label } from "@/components/ui/form-controls";
import { isErrorKey } from "./schemas";

/** Label + input + translated error, wired with aria-invalid / aria-describedby. */
export function TextField({
  id,
  label,
  error,
  hint,
  children,
  ...props
}: ComponentProps<"input"> & {
  id: string;
  label: string;
  error?: string;
  hint?: string;
  children?: ReactNode;
}) {
  const t = useTranslations("auth.errors");
  const message = isErrorKey(error) ? t(error) : undefined;
  const describedBy = [message && `${id}-error`, hint && `${id}-hint`].filter(Boolean).join(" ");
  return (
    <div className="flex flex-col gap-1.5">
      <Label htmlFor={id}>{label}</Label>
      <div className="relative">
        <Input
          id={id}
          aria-invalid={message ? true : undefined}
          aria-describedby={describedBy || undefined}
          {...props}
        />
        {children}
      </div>
      {hint && !message && (
        <p id={`${id}-hint`} className="text-xs text-muted-foreground">
          {hint}
        </p>
      )}
      <FieldError id={`${id}-error`} message={message} />
    </div>
  );
}

export function PasswordField(props: Parameters<typeof TextField>[0]) {
  const t = useTranslations("auth");
  const [visible, setVisible] = useState(false);
  return (
    <TextField {...props} type={visible ? "text" : "password"} className="pr-11">
      <button
        type="button"
        onClick={() => setVisible((v) => !v)}
        aria-label={visible ? t("hidePassword") : t("showPassword")}
        aria-pressed={visible}
        className="absolute right-1 top-1/2 flex size-9 -translate-y-1/2 items-center justify-center rounded-md text-muted-foreground hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
      >
        {visible ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
      </button>
    </TextField>
  );
}

export function SubmitButton({ pending, label }: { pending: boolean; label: string }) {
  const t = useTranslations("auth");
  return (
    <Button type="submit" size="lg" className="w-full" disabled={pending} aria-busy={pending}>
      {pending && <Loader2 className="animate-spin" aria-hidden="true" />}
      {pending ? t("submitting") : label}
    </Button>
  );
}

export function FormAlert({ message, focus = true }: { message: string | null; focus?: boolean }) {
  const ref = useRef<HTMLParagraphElement>(null);
  // Bring server errors into view (the alert sits above the fields).
  useEffect(() => {
    if (message && focus) {
      ref.current?.scrollIntoView({ block: "center", behavior: "smooth" });
      ref.current?.focus({ preventScroll: true });
    }
  }, [message, focus]);
  if (!message) return null;
  return (
    <p
      ref={ref}
      tabIndex={-1}
      role="alert"
      className="flex items-start gap-2 rounded-lg border border-warning/40 bg-warning/10 p-3 text-sm text-warning"
    >
      <AlertCircle className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
      {message}
    </p>
  );
}
