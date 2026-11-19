import { defineRouting } from "next-intl/routing";

// The platform is Russian-only. next-intl is kept so all UI texts stay in one
// messages file (src/locales/ru.json) and another language can be added later.
export const locales = ["ru"] as const;
export type Locale = (typeof locales)[number];

export const routing = defineRouting({
  locales,
  defaultLocale: "ru",
  // Clean URLs without a locale segment: /courses, /login, ...
  localePrefix: "never",
  localeDetection: false,
  localeCookie: false,
});
