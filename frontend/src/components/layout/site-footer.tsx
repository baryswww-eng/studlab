import { getTranslations } from "next-intl/server";
import { ContactList, SocialList } from "@/features/contacts/contact-info";
import { Link } from "@/i18n/navigation";
import { Logo } from "./logo";

const linkClass =
  "text-sm text-muted-foreground transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded";

export async function SiteFooter() {
  const t = await getTranslations();
  return (
    <footer className="mt-auto border-t border-border/70 bg-card/30">
      <div className="mx-auto grid max-w-6xl gap-10 px-4 py-12 sm:grid-cols-2 sm:px-6 lg:grid-cols-[1.4fr_1fr_1fr_1.2fr]">
        <div className="flex flex-col gap-3">
          <Logo />
          <p className="text-sm text-muted-foreground">{t("brand.slogan")}</p>
          <p className="text-sm text-muted-foreground">{t("brand.tagline")}</p>
        </div>

        <nav aria-labelledby="footer-platform" className="flex flex-col gap-2.5">
          <h2 id="footer-platform" className="mb-1 text-sm font-semibold">
            {t("footer.platform")}
          </h2>
          <Link href="/courses" className={linkClass}>
            {t("nav.courses")}
          </Link>
          <Link href="/about" className={linkClass}>
            {t("nav.about")}
          </Link>
          <Link href="/status" className={linkClass}>
            {t("footer.status")}
          </Link>
        </nav>

        <nav aria-labelledby="footer-legal" className="flex flex-col gap-2.5">
          <h2 id="footer-legal" className="mb-1 text-sm font-semibold">
            {t("footer.legal")}
          </h2>
          <Link href="/privacy" className={linkClass}>
            {t("footer.privacy")}
          </Link>
          <Link href="/terms" className={linkClass}>
            {t("footer.terms")}
          </Link>
        </nav>

        <div className="flex flex-col gap-2.5">
          <h2 className="mb-1 text-sm font-semibold">{t("footer.contact")}</h2>
          <ContactList />
          <h2 className="mb-1 mt-3 text-sm font-semibold">{t("footer.social")}</h2>
          <SocialList qrLabel={t("footer.qr")} />
        </div>
      </div>
      <div className="border-t border-border/70">
        <div className="mx-auto flex max-w-6xl flex-col items-start gap-3 px-4 py-5 text-sm text-muted-foreground sm:flex-row sm:items-center sm:justify-between sm:px-6">
          <p>{t("footer.rights", { year: new Date().getFullYear() })}</p>
        </div>
      </div>
    </footer>
  );
}
