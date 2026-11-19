import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { DashboardView } from "@/features/cabinet/dashboard-view";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("cabinet");
  return { title: t("nav.dashboard"), robots: { index: false } };
}

export default function Page() {
  return <DashboardView />;
}