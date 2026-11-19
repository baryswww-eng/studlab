import { z } from "zod";

/**
 * Validation rules shared by login/register forms. Messages are translation
 * KEYS (auth.errors.*) resolved in the UI, so schemas stay locale-independent.
 * The backend re-validates everything (Phase 3) — this is only for UX.
 */
export const loginSchema = z.object({
  email: z.string().trim().min(1, "required").pipe(z.email("email")),
  password: z.string().min(1, "required").max(128, "passwordMax"),
});

export const registerSchema = z
  .object({
    fullName: z.string().trim().min(2, "nameMin").max(120, "nameMax"),
    email: z.string().trim().min(1, "required").pipe(z.email("email")),
    password: z
      .string()
      .min(8, "passwordMin")
      .max(128, "passwordMax")
      .regex(/\p{L}/u, "passwordWeak")
      .regex(/\d/, "passwordWeak"),
    confirmPassword: z.string().min(1, "required"),
    acceptTerms: z.boolean().refine((v) => v, "terms"),
  })
  .refine((d) => d.password === d.confirmPassword, {
    path: ["confirmPassword"],
    message: "passwordMismatch",
  });

export type LoginValues = z.infer<typeof loginSchema>;
export type RegisterValues = z.infer<typeof registerSchema>;

export const ERROR_KEYS = [
  "required",
  "email",
  "nameMin",
  "nameMax",
  "passwordMin",
  "passwordMax",
  "passwordWeak",
  "passwordMismatch",
  "terms",
] as const;
export type ErrorKey = (typeof ERROR_KEYS)[number];

export function isErrorKey(value: string | undefined): value is ErrorKey {
  return ERROR_KEYS.includes(value as ErrorKey);
}
