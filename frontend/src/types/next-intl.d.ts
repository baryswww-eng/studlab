import type { routing } from "@/i18n/routing";
import type messages from "@/locales/ru.json";

// Strongly-typed translation keys for next-intl.
declare module "next-intl" {
  interface AppConfig {
    Locale: (typeof routing.locales)[number];
    Messages: typeof messages;
  }
}
