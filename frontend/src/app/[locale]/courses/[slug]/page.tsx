import {
  BookOpen,
  CheckCircle2,
  CircleHelp,
  ClipboardCheck,
  Clock,
  FileText,
  Info,
  MessageSquare,
  PlayCircle,
  SquarePen,
  UserRound,
} from "lucide-react";
import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { getFormatter, getTranslations, setRequestLocale } from "next-intl/server";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/states";
import { CourseCover } from "@/features/courses/category-icon";
import { durationParts, formatPrice } from "@/features/courses/format";
import { Link } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";
import { cn } from "@/lib/utils";
import { getCourse, safe } from "@/services/courses";
import type { LessonType } from "@/types/course";

// Course content is always: 1) theory, 2) video lessons, 3) tests & practical tasks.
const SECTION_KEYS = ["theory", "video", "practice"] as const;
const SECTION_ICON = { theory: BookOpen, video: PlayCircle, practice: ClipboardCheck } as const;
const SECTION_STYLE = {
  theory: "bg-accent/15 text-accent",
  video: "bg-primary/15 text-[#a996ff]",
  practice: "bg-success/15 text-success",
} as const;
const ACTION_LABEL: Record<LessonType, "read" | "watch" | "takeQuiz" | "solve"> = {
  text: "read",
  video: "watch",
  quiz: "takeQuiz",
  assignment: "solve",
};

const LESSON_ICON: Record<LessonType, typeof FileText> = {
  text: FileText,
  video: PlayCircle,
  quiz: CircleHelp,
  assignment: SquarePen,
};

export async function generateMetadata({
  params,
}: PageProps<"/[locale]/courses/[slug]">): Promise<Metadata> {
  const { locale, slug } = await params;
  const result = await safe(getCourse(locale as Locale, slug));
  if ("error" in result || !result.data) return {};
  return { title: result.data.title, description: result.data.short_description };
}

export default async function CoursePage({ params }: PageProps<"/[locale]/courses/[slug]">) {
  const { locale: raw, slug } = await params;
  const locale = raw as Locale;
  setRequestLocale(locale);

  const [t, format, result] = await Promise.all([
    getTranslations(),
    getFormatter(),
    safe(getCourse(locale, slug)),
  ]);

  if ("error" in result) {
    return (
      <div className="mx-auto w-full max-w-6xl px-4 py-16 sm:px-6">
        <ErrorState text={t("common.apiError")} />
      </div>
    );
  }
  const course = result.data;
  if (!course) notFound();

  const lessonsTotal = course.lessons_count;
  const price = formatPrice(format, course, t("common.free"));
  const allLessons = course.modules.flatMap((m) => m.lessons);
  const firstLesson = allLessons[0]; // start with theory

  return (
    <article>
      {/* Header */}
      <section className="border-b border-border bg-gradient-to-b from-primary/10 to-transparent">
        <div className="mx-auto grid w-full max-w-6xl gap-10 px-4 py-10 sm:px-6 lg:grid-cols-[1fr_360px] lg:py-14">
          <div className="flex flex-col gap-5">
            <nav aria-label="Breadcrumb" className="text-sm text-muted-foreground">
              <ol className="flex flex-wrap items-center gap-1.5">
                <li>
                  <Link href="/courses" className="hover:text-foreground">
                    {t("course.breadcrumb")}
                  </Link>
                </li>
                {course.category && (
                  <>
                    <li aria-hidden="true">/</li>
                    <li>
                      <Link
                        href={{ pathname: "/courses", query: { category: course.category.slug } }}
                        className="hover:text-foreground"
                      >
                        {course.category.name}
                      </Link>
                    </li>
                  </>
                )}
              </ol>
            </nav>
            <div className="flex flex-wrap gap-2">
              {course.is_demo && <Badge variant="warning">{t("common.demo")}</Badge>}
              <Badge variant="outline">{t(`common.level.${course.level}`)}</Badge>
              {course.is_free && <Badge variant="success">{t("common.free")}</Badge>}
            </div>
            <h1 className="text-3xl font-extrabold leading-tight tracking-tight text-balance sm:text-4xl">
              {course.title}
            </h1>
            <p className="max-w-2xl text-lg text-muted-foreground">{course.short_description}</p>
            <div className="flex flex-wrap gap-x-6 gap-y-2 text-sm text-muted-foreground">
              <span className="inline-flex items-center gap-1.5">
                <UserRound className="size-4" aria-hidden="true" />
                {course.instructor.full_name}
              </span>
              <span className="inline-flex items-center gap-1.5">
                <BookOpen className="size-4" aria-hidden="true" />
                {t("common.lessons", { count: lessonsTotal })}
              </span>
              <span className="inline-flex items-center gap-1.5">
                <Clock className="size-4" aria-hidden="true" />
                {t("common.duration", durationParts(course.duration_minutes))}
              </span>
            </div>
          </div>

          {/* Enroll card */}
          <aside className="h-fit overflow-hidden rounded-2xl border border-border bg-card shadow-xl lg:row-span-2">
            <CourseCover icon={course.category?.icon} title={course.title} coverUrl={course.cover_url} />
            <div className="flex flex-col gap-4 p-6">
              <p className={cn("text-3xl font-extrabold", course.is_free && "text-success")}>{price}</p>
              {firstLesson && (
                <Link
                  href={`/courses/${course.slug}/lessons/${firstLesson.id}`}
                  className={buttonVariants({ size: "lg", className: "w-full" })}
                >
                  <PlayCircle aria-hidden="true" />
                  {t("course.enroll")}
                </Link>
              )}
              <p className="text-center text-xs text-muted-foreground">{t("course.enrollHint")}</p>
            </div>
          </aside>
        </div>
      </section>

      <div className="mx-auto grid w-full max-w-6xl gap-10 px-4 py-12 sm:px-6 lg:grid-cols-[1fr_360px]">
        <div className="flex min-w-0 flex-col gap-10">
          {course.is_demo && (
            <p className="flex items-start gap-2 rounded-xl border border-warning/40 bg-warning/5 p-4 text-sm text-warning">
              <Info className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
              {t("course.demoNotice")}
            </p>
          )}

          {course.outcomes.length > 0 && (
            <section aria-labelledby="outcomes" className="rounded-2xl border border-border bg-card p-6">
              <h2 id="outcomes" className="text-xl font-bold">
                {t("course.outcomes")}
              </h2>
              <ul className="mt-4 grid gap-3 sm:grid-cols-2">
                {course.outcomes.map((item) => (
                  <li key={item} className="flex gap-2.5 text-sm">
                    <CheckCircle2 className="mt-0.5 size-4 shrink-0 text-success" aria-hidden="true" />
                    {item}
                  </li>
                ))}
              </ul>
            </section>
          )}

          <section aria-labelledby="about">
            <h2 id="about" className="text-xl font-bold">
              {t("course.about")}
            </h2>
            <p className="mt-3 whitespace-pre-line leading-7 text-foreground/90">{course.description}</p>
          </section>

          {course.requirements.length > 0 && (
            <section aria-labelledby="requirements">
              <h2 id="requirements" className="text-xl font-bold">
                {t("course.requirements")}
              </h2>
              <ul className="mt-3 list-disc space-y-1.5 pl-5 text-foreground/90 marker:text-accent">
                {course.requirements.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </section>
          )}

          <section aria-labelledby="curriculum">
            <div className="flex flex-wrap items-end justify-between gap-2">
              <h2 id="curriculum" className="text-xl font-bold">
                {t("course.curriculum")}
              </h2>
              <p className="text-sm text-muted-foreground">
                {t("course.curriculumSummary", { modules: course.modules.length, lessons: lessonsTotal })}
              </p>
            </div>
            <div className="mt-4 flex flex-col gap-5">
              {course.modules.map((module, index) => {
                const key = SECTION_KEYS[index] ?? "theory";
                const SectionIcon = SECTION_ICON[key];
                return (
                  <section
                    key={module.id}
                    aria-labelledby={`section-${module.id}`}
                    className="overflow-hidden rounded-2xl border border-border bg-card"
                  >
                    <header className="flex items-start gap-4 border-b border-border px-5 py-4">
                      <span
                        className={cn(
                          "flex size-10 shrink-0 items-center justify-center rounded-xl",
                          SECTION_STYLE[key],
                        )}
                      >
                        <SectionIcon className="size-5" aria-hidden="true" />
                      </span>
                      <div className="min-w-0 flex-1">
                        <h3 id={`section-${module.id}`} className="font-bold">
                          {index + 1}. {module.title}
                        </h3>
                        <p className="text-sm text-muted-foreground">{t(`course.sectionHints.${key}`)}</p>
                      </div>
                      <span className="shrink-0 text-sm text-muted-foreground">
                        {t("common.lessons", { count: module.lessons.length })}
                      </span>
                    </header>
                    <ul className="divide-y divide-border">
                      {module.lessons.map((lesson) => {
                        const Icon = LESSON_ICON[lesson.type];
                        return (
                          <li key={lesson.id}>
                            <Link
                              href={`/courses/${course.slug}/lessons/${lesson.id}`}
                              className="group flex items-center gap-3 px-5 py-3 text-sm transition-colors hover:bg-secondary/50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-ring"
                            >
                              <Icon className="size-4 shrink-0 text-accent" aria-hidden="true" />
                              <span className="sr-only">{t(`course.lessonType.${lesson.type}`)}:</span>
                              <span className="min-w-0 flex-1 group-hover:text-foreground">{lesson.title}</span>
                              <Badge variant="outline" className="hidden sm:inline-flex">
                                {t(`course.${ACTION_LABEL[lesson.type]}`)}
                              </Badge>
                              <span className="w-16 shrink-0 text-right text-muted-foreground">
                                {t("common.duration", durationParts(lesson.duration_minutes))}
                              </span>
                            </Link>
                          </li>
                        );
                      })}
                    </ul>
                  </section>
                );
              })}
            </div>          </section>

          <section aria-labelledby="reviews">
            <h2 id="reviews" className="text-xl font-bold">
              {t("course.reviews")}
            </h2>
            <p className="mt-3 flex items-center gap-2 rounded-xl border border-dashed border-border p-5 text-sm text-muted-foreground">
              <MessageSquare className="size-4" aria-hidden="true" />
              {t("course.noReviews")}
            </p>
          </section>
        </div>

        <aside aria-labelledby="instructor" className="h-fit rounded-2xl border border-border bg-card p-6">
          <h2 id="instructor" className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
            {t("course.instructor")}
          </h2>
          <div className="mt-4 flex items-center gap-3">
            <span className="flex size-12 items-center justify-center rounded-full bg-gradient-to-br from-primary to-accent text-lg font-bold text-white">
              {course.instructor.full_name.charAt(0)}
            </span>
            <div>
              <p className="font-semibold">{course.instructor.full_name}</p>
              {course.instructor.headline && (
                <p className="text-sm text-muted-foreground">{course.instructor.headline}</p>
              )}
            </div>
          </div>
          {course.instructor.bio && (
            <p className="mt-4 text-sm text-muted-foreground">{course.instructor.bio}</p>
          )}
        </aside>
      </div>
    </article>
  );
}
