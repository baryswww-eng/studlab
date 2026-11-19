import { FileWarning } from "lucide-react";
import { getTranslations } from "next-intl/server";

export async function LegalPage({ kind }: { kind: "privacy" | "terms" }) {
  const t = await getTranslations("legal");
  return (
    <div className="mx-auto w-full max-w-3xl px-4 py-14 sm:px-6">
      <h1 className="text-3xl font-extrabold tracking-tight">{t(`${kind}Title`)}</h1>
      <p className="mt-5 flex items-start gap-2 rounded-xl border border-warning/40 bg-warning/5 p-4 text-sm text-warning">
        <FileWarning className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
        {t("draft")}
      </p>
      <ol className="mt-8 flex list-decimal flex-col gap-4 pl-5 leading-7 text-foreground/90 marker:font-semibold marker:text-accent">
        {(["1", "2", "3", "4"] as const).map((k) => (
          <li key={k}>{t(`${kind}.${k}`)}</li>
        ))}
      </ol>
    </div>
  );
}
