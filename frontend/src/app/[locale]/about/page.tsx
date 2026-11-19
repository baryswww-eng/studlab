import { CheckCircle2 } from "lucide-react";
import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import type { Locale } from "@/i18n/routing";
import { ContactList, SocialList } from "@/features/contacts/contact-info";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("about");
  return { title: t("title"), description: t("lead") };
}

export default async function AboutPage({ params }: PageProps<"/[locale]/about">) {
  const { locale } = await params;
  setRequestLocale(locale as Locale);
  const t = await getTranslations("about");

  return (
    <div className="mx-auto w-full max-w-3xl px-4 py-14 sm:px-6">
      <h1 className="text-3xl font-extrabold tracking-tight sm:text-4xl">{t("title")}</h1>
      <p className="mt-4 text-lg text-muted-foreground">{t("lead")}</p>

      <section className="mt-10 rounded-2xl border border-border bg-gradient-to-br from-primary/15 to-card p-6">
        <h2 className="text-xl font-bold">{t("missionTitle")}</h2>
        <p className="mt-2 text-foreground/90">{t("mission")}</p>
      </section>

      <section className="mt-10">
        <h2 className="text-xl font-bold">{t("offerTitle")}</h2>
        <ul className="mt-4 flex flex-col gap-3">
          {(["1", "2", "3", "4"] as const).map((k) => (
            <li key={k} className="flex gap-3">
              <CheckCircle2 className="mt-0.5 size-5 shrink-0 text-success" aria-hidden="true" />
              {t(`offer.${k}`)}
            </li>
          ))}
        </ul>
      </section>

      <section className="mt-10">
        <h2 className="text-xl font-bold">{t("statusTitle")}</h2>
        <p className="mt-2 text-muted-foreground">{t("status")}</p>
      </section>

      <section id="contact" className="mt-10">
        <h2 className="text-xl font-bold">{t("contactTitle")}</h2>
        <div className="mt-3 grid gap-6 sm:grid-cols-2">
          <ContactList />
          <SocialList qrLabel={t("qr")} />
        </div>
      </section>
    </div>
  );
}
