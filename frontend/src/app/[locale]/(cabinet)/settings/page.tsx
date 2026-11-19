import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { SettingsView } from "@/features/cabinet/settings-view";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("cabinet");
  return { title: t("nav.settings"), robots: { index: false } };
}

export default function Page() {
  return <SettingsView />;
}