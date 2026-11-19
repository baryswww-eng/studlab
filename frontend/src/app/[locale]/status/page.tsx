import type { Metadata } from "next";
import { connection } from "next/server";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { Suspense } from "react";
import { Skeleton } from "@/components/ui/states";
import { StatusPanel } from "@/features/system-status/status-panel";
import type { Locale } from "@/i18n/routing";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("status");
  return { title: t("title"), robots: { index: false } };
}

async function LiveStatus() {
  // Health checks must run per request, never at build time.
  await connection();
  return <StatusPanel />;
}

export default async function StatusPage({ params }: PageProps<"/[locale]/status">) {
  const { locale } = await params;
  setRequestLocale(locale as Locale);
  return (
    <div className="mx-auto w-full max-w-2xl px-4 py-14 sm:px-6">
      <Suspense fallback={<Skeleton className="h-96 w-full rounded-2xl" />}>
        <LiveStatus />
      </Suspense>
    </div>
  );
}
