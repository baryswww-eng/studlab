import { ApiError, apiFetch } from "@/lib/api";
import type { Locale } from "@/i18n/routing";
import type {
  Category,
  CourseCard,
  CourseDetail,
  CourseQuery,
  LessonDetail,
  Page,
  PublicStats,
} from "@/types/course";

// Catalog content changes rarely; cache briefly on the Next.js server.
const REVALIDATE = { next: { revalidate: 30 } } as const;

function toQuery(params: Record<string, string | number | boolean | undefined>) {
  const search = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") search.set(key, String(value));
  }
  return search.toString();
}

export function listCourses(locale: Locale, query: CourseQuery = {}) {
  return apiFetch<Page<CourseCard>>(`/courses?${toQuery({ locale, ...query })}`, REVALIDATE);
}

export function listCategories(locale: Locale) {
  return apiFetch<Category[]>(`/categories?${toQuery({ locale })}`, REVALIDATE);
}

export function getPublicStats() {
  return apiFetch<PublicStats>("/stats/public", REVALIDATE);
}

/** Returns null when the course does not exist (404); other errors propagate. */
export async function getCourse(locale: Locale, slug: string): Promise<CourseDetail | null> {
  try {
    return await apiFetch<CourseDetail>(
      `/courses/${encodeURIComponent(slug)}?${toQuery({ locale })}`,
      REVALIDATE,
    );
  } catch (error) {
    if (error instanceof ApiError && (error.status === 404 || error.status === 422)) return null;
    throw error;
  }
}

/** Public lesson (no enrollment needed). Returns null on 404. */
export async function getLesson(locale: Locale, lessonId: number): Promise<LessonDetail | null> {
  try {
    return await apiFetch<LessonDetail>(`/lessons/${lessonId}?${toQuery({ locale })}`, REVALIDATE);
  } catch (error) {
    if (error instanceof ApiError && (error.status === 404 || error.status === 422)) return null;
    throw error;
  }
}

/** Wraps a request so a failing backend renders an error state instead of crashing the page. */
export async function safe<T>(promise: Promise<T>): Promise<{ data: T } | { error: true }> {
  try {
    return { data: await promise };
  } catch {
    return { error: true };
  }
}
