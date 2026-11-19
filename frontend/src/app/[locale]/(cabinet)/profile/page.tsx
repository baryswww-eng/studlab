import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { ProfileView } from "@/features/cabinet/profile-view";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("cabinet");
  return { title: t("nav.profile"), robots: { index: false } };
}

export default function Page() {
  return <ProfileView />;
}