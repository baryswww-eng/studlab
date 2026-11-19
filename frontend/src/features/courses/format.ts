import type { useFormatter } from "next-intl";

type Formatter = ReturnType<typeof useFormatter>;

/** Free label or a localized currency amount, e.g. "9 900 ₸". */
export function formatPrice(
  format: Formatter,
  course: { price: string; currency: string; is_free: boolean },
  freeLabel: string,
) {
  if (course.is_free) return freeLabel;
  return format.number(Number(course.price), {
    style: "currency",
    currency: course.currency,
    currencyDisplay: "narrowSymbol", // "₸" instead of "KZT"
    maximumFractionDigits: 0,
  });
}

/** Values for the `common.duration` message: t("common.duration", durationParts(m)). */
export function durationParts(totalMinutes: number) {
  return { hours: Math.floor(totalMinutes / 60), minutes: totalMinutes % 60 };
}
