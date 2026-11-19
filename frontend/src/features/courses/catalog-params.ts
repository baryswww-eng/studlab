import type { CourseLevel, CourseQuery, CourseSort, PriceFilter } from "@/types/course";

export const LEVELS: CourseLevel[] = ["beginner", "intermediate", "advanced"];
export const PRICES: PriceFilter[] = ["free", "paid"];
export const SORTS: CourseSort[] = ["newest", "title", "price_asc", "price_desc"];
export const PAGE_SIZE = 9;

type RawParams = Record<string, string | string[] | undefined>;

function one(value: string | string[] | undefined): string | undefined {
  return Array.isArray(value) ? value[0] : value;
}

function pick<T extends string>(value: string | undefined, allowed: readonly T[]): T | undefined {
  return allowed.includes(value as T) ? (value as T) : undefined;
}

/** Validates untrusted URL search params into a typed catalog query. */
export function parseCatalogParams(raw: RawParams): Required<Pick<CourseQuery, "page">> & CourseQuery {
  const q = one(raw.q)?.trim().slice(0, 100) || undefined;
  const category = one(raw.category);
  const page = Number.parseInt(one(raw.page) ?? "1", 10);
  return {
    q,
    category: category && /^[a-z0-9-]{1,80}$/.test(category) ? category : undefined,
    level: pick(one(raw.level), LEVELS),
    price: pick(one(raw.price), PRICES),
    sort: pick(one(raw.sort), SORTS),
    page: Number.isFinite(page) && page > 0 && page <= 10_000 ? page : 1,
  };
}
