"use client";

import { Search, X } from "lucide-react";
import { useTranslations } from "next-intl";
import { useSearchParams } from "next/navigation";
import { useEffect, useRef, useState, useTransition } from "react";
import { Button } from "@/components/ui/button";
import { Input, Label, Select } from "@/components/ui/form-controls";
import { usePathname, useRouter } from "@/i18n/navigation";
import type { Category } from "@/types/course";
import { LEVELS, SORTS } from "./catalog-params";

const SORT_LABEL = {
  newest: "sortNewest",
  title: "sortTitle",
  price_asc: "sortPriceAsc",
  price_desc: "sortPriceDesc",
} as const;

/**
 * Filters live in the URL (?q=&category=&level=&price=&sort=), so results are
 * shareable and survive reloads. Without JS the form still works via GET submit.
 */
export function CatalogFilters({ categories }: { categories: Category[] }) {
  const t = useTranslations("catalog");
  const tc = useTranslations("common");
  const router = useRouter();
  const pathname = usePathname();
  const params = useSearchParams();
  const [isPending, startTransition] = useTransition();
  const urlQuery = params.get("q") ?? "";
  const [query, setQuery] = useState(urlQuery);
  const [syncedQuery, setSyncedQuery] = useState(urlQuery);
  const debounce = useRef<ReturnType<typeof setTimeout>>(undefined);

  // Keep the input in sync when the URL changes elsewhere (e.g. "reset" link, back button).
  if (urlQuery !== syncedQuery) {
    setSyncedQuery(urlQuery);
    setQuery(urlQuery);
  }

  function update(key: string, value: string) {
    const next = new URLSearchParams(params.toString());
    if (value) next.set(key, value);
    else next.delete(key);
    next.delete("page"); // any filter change resets pagination
    const search = next.toString();
    startTransition(() => router.replace(search ? `${pathname}?${search}` : pathname, { scroll: false }));
  }

  useEffect(() => () => clearTimeout(debounce.current), []);

  function onSearchChange(value: string) {
    setQuery(value);
    clearTimeout(debounce.current);
    debounce.current = setTimeout(() => update("q", value.trim()), 350);
  }

  const hasFilters = ["q", "category", "level", "sort"].some((k) => params.has(k));

  return (
    <form
      role="search"
      method="get"
      aria-busy={isPending}
      onSubmit={(e) => {
        e.preventDefault();
        clearTimeout(debounce.current);
        update("q", query.trim());
      }}
      className="grid gap-4 rounded-2xl border border-border bg-card p-4 sm:p-5 md:grid-cols-2 lg:grid-cols-[2fr_1fr_1fr_1fr]"
    >
      <div className="flex flex-col gap-1.5 md:col-span-2 lg:col-span-1">
        <Label htmlFor="catalog-q">{t("searchLabel")}</Label>
        <div className="relative">
          <Search
            aria-hidden="true"
            className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
          />
          <Input
            id="catalog-q"
            name="q"
            type="search"
            value={query}
            maxLength={100}
            placeholder={t("searchPlaceholder")}
            onChange={(e) => onSearchChange(e.target.value)}
            className="pl-9"
          />
        </div>
      </div>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="catalog-category">{t("category")}</Label>
        <Select
          id="catalog-category"
          name="category"
          value={params.get("category") ?? ""}
          onChange={(e) => update("category", e.target.value)}
        >
          <option value="">{t("allCategories")}</option>
          {categories.map((c) => (
            <option key={c.slug} value={c.slug}>
              {c.name}
            </option>
          ))}
        </Select>
      </div>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="catalog-level">{t("level")}</Label>
        <Select
          id="catalog-level"
          name="level"
          value={params.get("level") ?? ""}
          onChange={(e) => update("level", e.target.value)}
        >
          <option value="">{t("allLevels")}</option>
          {LEVELS.map((level) => (
            <option key={level} value={level}>
              {tc(`level.${level}`)}
            </option>
          ))}
        </Select>
      </div>


      <div className="flex flex-col gap-1.5">
        <Label htmlFor="catalog-sort">{t("sort")}</Label>
        <Select
          id="catalog-sort"
          name="sort"
          value={params.get("sort") ?? "newest"}
          onChange={(e) => update("sort", e.target.value === "newest" ? "" : e.target.value)}
        >
          {SORTS.map((s) => (
            <option key={s} value={s}>
              {t(SORT_LABEL[s])}
            </option>
          ))}
        </Select>
      </div>

      {hasFilters && (
        <div className="md:col-span-2 lg:col-span-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setQuery("");
              startTransition(() => router.replace(pathname, { scroll: false }));
            }}
          >
            <X aria-hidden="true" />
            {t("reset")}
          </Button>
        </div>
      )}
    </form>
  );
}
