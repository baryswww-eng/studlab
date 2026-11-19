import type { Metadata } from "next";
import { getTranslations } from "next-intl/server";
import { MyCoursesView } from "@/features/cabinet/dashboard-view";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("cabinet");
  return { title: t("nav.myCourses"), robots: { index: false } };
}

export default function Page() {
  return <MyCoursesView />;
}