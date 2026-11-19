import { Sparkles } from "lucide-react";
import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { AIChat } from "@/features/ai/ai-chat";
import type { Locale } from "@/i18n/routing";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("ai");
  return { title: t("title"), description: t("subtitle") };
}

export default async function AITutorPage({ params }: PageProps<"/[locale]/ai-tutor">) {
  const { locale } = await params;
  setRequestLocale(locale as Locale);
  const t = await getTranslations("ai");
  return (
    <div className="mx-auto w-full max-w-4xl px-4 py-10 sm:px-6">
      <header className="mb-6 flex flex-col gap-2">
        <h1 className="flex items-center gap-3 text-3xl font-extrabold tracking-tight">
          <span className="flex size-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary to-accent text-white">
            <Sparkles className="size-5" aria-hidden="true" />
          </span>
          {t("title")}
        </h1>
        <p className="text-muted-foreground">{t("subtitle")}</p>
      </header>
      <AIChat />
    </div>
  );
}
