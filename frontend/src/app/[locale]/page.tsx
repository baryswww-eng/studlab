import {
  ArrowRight,
  Award,
  BookOpenCheck,
  Bot,
  Compass,
  Languages,
  LineChart,
  Quote,
  Rocket,
  UserPlus,
  Wrench,
} from "lucide-react";
import type { Metadata } from "next";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { EmptyState, ErrorState, SectionHeading } from "@/components/ui/states";
import { CategoryIcon, categoryGradient } from "@/features/courses/category-icon";
import { CourseCard } from "@/features/courses/course-card";
import { HeroIllustration } from "@/features/landing/hero-illustration";
import { Link } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";
import { cn } from "@/lib/utils";
import { getPublicStats, listCategories, listCourses, safe } from "@/services/courses";

export async function generateMetadata(): Promise<Metadata> {
  const t = await getTranslations("meta");
  return { title: { absolute: t("title") } };
}

const BENEFITS = [
  { key: "language", icon: Languages, soon: false },
  { key: "practice", icon: Wrench, soon: false },
  { key: "progress", icon: LineChart, soon: false },
  { key: "ai", icon: Bot, soon: false },
  { key: "certificates", icon: Award, soon: true },
] as const;

const STEPS = [
  { key: "1", icon: UserPlus },
  { key: "2", icon: Compass },
  { key: "3", icon: BookOpenCheck },
  { key: "4", icon: Rocket },
] as const;

export default async function HomePage({ params }: PageProps<"/[locale]">) {
  const { locale: raw } = await params;
  const locale = raw as Locale;
  setRequestLocale(locale);

  const [t, featured, categories, stats] = await Promise.all([
    getTranslations(),
    safe(listCourses(locale, { featured: true, page_size: 6 })),
    safe(listCategories(locale)),
    safe(getPublicStats()),
  ]);

  const container = "mx-auto w-full max-w-6xl px-4 sm:px-6";

  return (
    <>
      {/* 1. Hero */}
      <section className="relative isolate overflow-hidden">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute -top-40 left-1/2 -z-10 h-[34rem] w-[60rem] -translate-x-1/2 rounded-full bg-gradient-to-r from-primary/25 via-accent/10 to-primary/20 blur-3xl"
        />
        <div className={cn(container, "grid items-center gap-14 py-16 lg:grid-cols-2 lg:py-24")}>
          <div className="flex min-w-0 flex-col gap-6">
            <Badge variant="accent" className="w-fit px-3 py-1">
              {t("home.hero.eyebrow")}
            </Badge>
            {/* Long words ("программирование"): size steps + hyphenation keep them inside the column. */}
            <h1 className="text-[2rem] font-extrabold leading-[1.1] tracking-tight text-balance hyphens-auto break-words min-[400px]:text-4xl sm:text-5xl lg:text-[2.6rem] xl:text-[3.25rem]">
              {t("home.hero.title")}
            </h1>
            <p className="max-w-xl text-lg text-muted-foreground text-pretty">
              {t("home.hero.subtitle")}
            </p>
            <div className="flex flex-wrap gap-3">
              <Link href="/courses" className={buttonVariants({ size: "lg" })}>
                {t("home.hero.cta")}
                <ArrowRight />
              </Link>
              <Link href="/register" className={buttonVariants({ size: "lg", variant: "outline" })}>
                {t("home.hero.secondary")}
              </Link>
            </div>
          </div>
          <HeroIllustration />
        </div>
      </section>

      {/* 2. Featured courses */}
      <section aria-labelledby="featured" className={cn(container, "py-14")}>
        <SectionHeading
          id="featured"
          title={t("home.featured.title")}
          subtitle={t("home.featured.subtitle")}
          action={
            <Link href="/courses" className={buttonVariants({ variant: "outline", size: "sm" })}>
              {t("home.featured.all")}
              <ArrowRight />
            </Link>
          }
        />
        {"error" in featured ? (
          <ErrorState text={t("common.apiError")} />
        ) : featured.data.items.length === 0 ? (
          <EmptyState title={t("home.featured.empty")} />
        ) : (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {featured.data.items.map((course) => (
              <CourseCard key={course.id} course={course} />
            ))}
          </div>
        )}
      </section>

      {/* 3. Directions */}
      <section aria-labelledby="directions" className={cn(container, "py-14")}>
        <SectionHeading
          id="directions"
          title={t("home.directions.title")}
          subtitle={t("home.directions.subtitle")}
        />
        {"error" in categories ? (
          <ErrorState text={t("common.apiError")} />
        ) : (
          <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {categories.data.map((c) => (
              <li key={c.id}>
                <Link
                  href={{ pathname: "/courses", query: { category: c.slug } }}
                  className="group flex items-center gap-4 rounded-2xl border border-border bg-card p-5 transition-colors hover:border-primary/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                >
                  <span
                    className={cn(
                      "flex size-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br text-white",
                      categoryGradient(c.icon),
                    )}
                  >
                    <CategoryIcon icon={c.icon} className="size-6" />
                  </span>
                  <span className="flex flex-col">
                    <span className="font-semibold">{c.name}</span>
                    <span className="text-sm text-muted-foreground">
                      {t("home.directions.count", { count: c.course_count })}
                    </span>
                  </span>
                  <ArrowRight
                    aria-hidden="true"
                    className="ml-auto size-5 text-muted-foreground transition-transform group-hover:translate-x-1 group-hover:text-foreground"
                  />
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      {/* 4. Benefits */}
      <section aria-labelledby="benefits" className={cn(container, "py-14")}>
        <SectionHeading id="benefits" title={t("home.benefits.title")} />
        <ul className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
          {BENEFITS.map(({ key, icon: Icon, soon }) => (
            <li key={key} className="flex flex-col gap-3 rounded-2xl border border-border bg-card p-5">
              <div className="flex items-center justify-between">
                <span className="flex size-10 items-center justify-center rounded-lg bg-primary/15 text-[#a996ff]">
                  <Icon className="size-5" aria-hidden="true" />
                </span>
                {soon && <Badge variant="outline">{t("common.soon")}</Badge>}
              </div>
              <h3 className="font-semibold">{t(`home.benefits.items.${key}.title`)}</h3>
              <p className="text-sm text-muted-foreground">{t(`home.benefits.items.${key}.text`)}</p>
            </li>
          ))}
        </ul>
      </section>

      {/* 5. How it works */}
      <section aria-labelledby="steps" className={cn(container, "py-14")}>
        <SectionHeading id="steps" title={t("home.steps.title")} />
        <ol className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {STEPS.map(({ key, icon: Icon }) => (
            <li key={key} className="relative flex flex-col gap-3 rounded-2xl border border-border bg-card p-5">
              <span className="absolute right-5 top-4 text-4xl font-extrabold text-border">{key}</span>
              <span className="flex size-10 items-center justify-center rounded-lg bg-accent/15 text-accent">
                <Icon className="size-5" aria-hidden="true" />
              </span>
              <h3 className="font-semibold">{t(`home.steps.items.${key}.title`)}</h3>
              <p className="text-sm text-muted-foreground">{t(`home.steps.items.${key}.text`)}</p>
            </li>
          ))}
        </ol>
      </section>

      {/* 6. Stats — only real numbers from the database */}
      {"data" in stats && (
        <section aria-labelledby="stats" className={cn(container, "py-14")}>
          <div className="rounded-3xl border border-border bg-gradient-to-br from-primary/15 via-card to-accent/10 p-8 sm:p-10">
            <h2 id="stats" className="text-2xl font-bold tracking-tight sm:text-3xl">
              {t("home.stats.title")}
            </h2>
            <dl className="mt-8 grid gap-6 sm:grid-cols-3">
              {(
                [
                  ["courses", stats.data.published_courses],
                  ["categories", stats.data.categories],
                  ["lessons", stats.data.lessons],
                ] as const
              ).map(([key, value]) => (
                <div key={key} className="flex flex-col gap-1">
                  <dt className="order-2 text-sm text-muted-foreground">{t(`home.stats.${key}`)}</dt>
                  <dd className="order-1 text-4xl font-extrabold tracking-tight">{value}</dd>
                </div>
              ))}
            </dl>
            <p className="mt-6 text-xs text-muted-foreground">{t("home.stats.note")}</p>
          </div>
        </section>
      )}

      {/* 7. Testimonials — demo, clearly labelled */}
      <section aria-labelledby="testimonials" className={cn(container, "py-14")}>
        <SectionHeading id="testimonials" title={t("home.testimonials.title")} />
        <ul className="grid gap-4 md:grid-cols-3">
          {(["1", "2", "3"] as const).map((key) => (
            <li key={key} className="flex flex-col gap-4 rounded-2xl border border-dashed border-border bg-card p-6">
              <div className="flex items-center justify-between">
                <Quote className="size-6 text-primary" aria-hidden="true" />
                <Badge variant="warning">{t("common.demo")}</Badge>
              </div>
              <blockquote className="text-sm text-foreground/90">
                {t(`home.testimonials.items.${key}.text`)}
              </blockquote>
              <p className="mt-auto text-sm">
                <span className="font-semibold">{t(`home.testimonials.items.${key}.name`)}</span>
                <span className="text-muted-foreground"> · {t(`home.testimonials.items.${key}.role`)}</span>
              </p>
            </li>
          ))}
        </ul>
        <p className="mt-4 text-xs text-muted-foreground">{t("home.testimonials.demoNote")}</p>
      </section>

      {/* CTA */}
      <section className={cn(container, "pb-20 pt-6")}>
        <div className="flex flex-col items-start gap-5 rounded-3xl bg-gradient-to-r from-primary to-[#5b8cff] p-8 sm:flex-row sm:items-center sm:justify-between sm:p-10">
          <div>
            <h2 className="text-2xl font-bold text-white sm:text-3xl">{t("home.cta.title")}</h2>
            <p className="mt-2 text-white/85">{t("home.cta.text")}</p>
          </div>
          <Link
            href="/courses"
            className={cn(buttonVariants({ size: "lg" }), "bg-white text-[#101827] hover:bg-white/90")}
          >
            {t("home.cta.button")}
            <ArrowRight />
          </Link>
        </div>
      </section>
    </>
  );
}
