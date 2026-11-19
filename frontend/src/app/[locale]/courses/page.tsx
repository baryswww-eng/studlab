import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { Suspense } from "react";
import { buttonVariants } from "@/components/ui/button";
import { EmptyState, ErrorState } from "@/components/ui/states";
import { CatalogFilters } from "@/features/courses/catalog-filters";
import { PAGE_SIZE, parseCatalogParams } from "@/features/courses/catalog-params";
import { CourseCard } from "@/features/courses/course-card";
import { Pagination } from "@/features/courses/pagination";
import { Link } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";
import { listCategories, listCourses, safe } from "@/services/courses";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("catalog");
  return { title: t("title"), description: t("subtitle") };
}

export default async function CoursesPage({ params, searchParams }: PageProps<"/[locale]/courses">) {
  const { locale: raw } = await params;
  const locale = raw as Locale;
  setRequestLocale(locale);

  const query = parseCatalogParams(await searchParams);
  const [t, courses, categories] = await Promise.all([
    getTranslations("catalog"),
    safe(listCourses(locale, { ...query, page_size: PAGE_SIZE })),
    safe(listCategories(locale)),
  ]);
  const tc = await getTranslations("common");

  return (
    <div className="mx-auto w-full max-w-6xl px-4 py-12 sm:px-6">
      <header className="mb-8 flex flex-col gap-2">
        <h1 className="text-3xl font-extrabold tracking-tight sm:text-4xl">{t("title")}</h1>
        <p className="text-muted-foreground">{t("subtitle")}</p>
      </header>

      <Suspense>
        <CatalogFilters categories={"data" in categories ? categories.data : []} />
      </Suspense>

      <section aria-live="polite" className="mt-8">
        {"error" in courses ? (
          <ErrorState
            text={tc("apiError")}
            action={
              <Link href="/courses" className={buttonVariants({ variant: "outline", size: "sm" })}>
                {tc("retry")}
              </Link>
            }
          />
        ) : courses.data.total === 0 ? (
          <EmptyState
            title={t("empty.title")}
            text={t("empty.text")}
            action={
              <Link href="/courses" className={buttonVariants({ variant: "outline", size: "sm" })}>
                {t("reset")}
              </Link>
            }
          />
        ) : (
          <>
            <p className="mb-5 text-sm text-muted-foreground">
              {t("results", { count: courses.data.total })}
            </p>
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {courses.data.items.map((course) => (
                <CourseCard key={course.id} course={course} />
              ))}
            </div>
            <Pagination
              page={courses.data.page}
              pages={courses.data.pages}
              query={{
                q: query.q,
                category: query.category,
                level: query.level,
                price: query.price,
                sort: query.sort,
              }}
            />
          </>
        )}
      </section>
    </div>
  );
}
