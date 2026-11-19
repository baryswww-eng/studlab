import { ChevronLeft, ChevronRight } from "lucide-react";
import { useTranslations } from "next-intl";
import { buttonVariants } from "@/components/ui/button";
import { Link } from "@/i18n/navigation";
import { cn } from "@/lib/utils";

export function Pagination({
  page,
  pages,
  query,
}: {
  page: number;
  pages: number;
  query: Record<string, string | undefined>;
}) {
  const t = useTranslations("catalog.pagination");
  if (pages <= 1) return null;

  const href = (p: number) => {
    const q: Record<string, string> = {};
    for (const [k, v] of Object.entries(query)) if (v) q[k] = v;
    if (p > 1) q.page = String(p);
    return { pathname: "/courses" as const, query: q };
  };
  const disabled = "pointer-events-none opacity-40";

  return (
    <nav aria-label={t("label")} className="mt-10 flex items-center justify-center gap-3">
      <Link
        href={href(page - 1)}
        aria-disabled={page <= 1}
        tabIndex={page <= 1 ? -1 : undefined}
        className={cn(buttonVariants({ variant: "outline", size: "sm" }), page <= 1 && disabled)}
      >
        <ChevronLeft aria-hidden="true" />
        {t("prev")}
      </Link>
      <span className="text-sm text-muted-foreground" aria-current="page">
        {t("page", { page, pages })}
      </span>
      <Link
        href={href(page + 1)}
        aria-disabled={page >= pages}
        tabIndex={page >= pages ? -1 : undefined}
        className={cn(buttonVariants({ variant: "outline", size: "sm" }), page >= pages && disabled)}
      >
        {t("next")}
        <ChevronRight aria-hidden="true" />
      </Link>
    </nav>
  );
}
