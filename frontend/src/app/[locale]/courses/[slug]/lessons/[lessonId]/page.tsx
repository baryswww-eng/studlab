import { ArrowLeft, ArrowRight, ExternalLink, Sparkles } from "lucide-react";
import type { Metadata } from "next";
import { notFound, redirect } from "next/navigation";
import { getTranslations, setRequestLocale } from "next-intl/server";
import { buttonVariants } from "@/components/ui/button";
import { ErrorState } from "@/components/ui/states";
import { AIChat } from "@/features/ai/ai-chat";
import { LessonBody } from "@/features/lessons/lesson-body";
import { YouTubePlayer } from "@/features/lessons/youtube-player";
import {
  CourseProgressProvider,
  LessonCompleteButton,
  LessonOutlineNav,
} from "@/features/progress/course-progress";
import { Link } from "@/i18n/navigation";
import type { Locale } from "@/i18n/routing";
import { getLesson, safe } from "@/services/courses";

function parseId(raw: string) {
  return /^\d{1,9}$/.test(raw) ? Number(raw) : null;
}

export async function generateMetadata({
  params,
}: PageProps<"/[locale]/courses/[slug]/lessons/[lessonId]">): Promise<Metadata> {
  const { locale, lessonId } = await params;
  const id = parseId(lessonId);
  const result = id ? await safe(getLesson(locale as Locale, id)) : null;
  if (!result || "error" in result || !result.data) return {};
  return { title: `${result.data.title} — ${result.data.course.title}` };
}

export default async function LessonPage({
  params,
}: PageProps<"/[locale]/courses/[slug]/lessons/[lessonId]">) {
  const { locale: raw, slug, lessonId } = await params;
  const locale = raw as Locale;
  setRequestLocale(locale);
  const id = parseId(lessonId);
  if (!id) notFound();

  const [t, result] = await Promise.all([getTranslations(), safe(getLesson(locale, id))]);
  if ("error" in result) {
    return (
      <div className="mx-auto w-full max-w-6xl px-4 py-16 sm:px-6">
        <ErrorState text={t("common.apiError")} />
      </div>
    );
  }
  const lesson = result.data;
  if (!lesson) notFound();
  // Canonical URL: the lesson must belong to the course in the path.
  if (lesson.course.slug !== slug) redirect(`/courses/${lesson.course.slug}/lessons/${lesson.id}`);

  const lessonHref = (lid: number) => `/courses/${lesson.course.slug}/lessons/${lid}`;

  return (
    <CourseProgressProvider slug={lesson.course.slug}>
      <div className="mx-auto grid w-full max-w-7xl gap-8 px-4 py-8 sm:px-6 lg:grid-cols-[1fr_340px]">
        <div className="flex min-w-0 flex-col gap-5">
          <nav aria-label="Breadcrumb" className="text-sm text-muted-foreground">
            <ol className="flex flex-wrap items-center gap-1.5">
              <li>
                <Link href="/courses" className="hover:text-foreground">
                  {t("course.breadcrumb")}
                </Link>
              </li>
              <li aria-hidden="true">/</li>
              <li>
                <Link href={`/courses/${lesson.course.slug}`} className="hover:text-foreground">
                  {lesson.course.title}
                </Link>
              </li>
            </ol>
          </nav>

          <header>
            <p className="text-sm font-medium text-accent">
              {lesson.module_title}
              {lesson.type === "text" && <> · {t("lesson.readTime", { minutes: lesson.duration_minutes })}</>}
            </p>
            <h1 className="mt-1 text-2xl font-extrabold tracking-tight sm:text-3xl">{lesson.title}</h1>
          </header>

          {lesson.youtube_id ? (
            <>
              <YouTubePlayer
                videoId={lesson.youtube_id}
                title={t("lesson.playerTitle", { title: lesson.title })}
              />
              <div className="flex flex-wrap items-center justify-between gap-2 text-sm text-muted-foreground">
                {lesson.video_author && <span>{t("lesson.videoBy", { author: lesson.video_author })}</span>}
                <a
                  href={`https://www.youtube.com/watch?v=${lesson.youtube_id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 hover:text-foreground"
                >
                  {t("lesson.openOnYoutube")}
                  <ExternalLink className="size-3.5" aria-hidden="true" />
                </a>
              </div>
            </>
          ) : (
            <LessonBody lessonId={lesson.id} type={lesson.type} content={lesson.content_md} />
          )}

          <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-border bg-card p-4">
            {lesson.type === "text" || lesson.type === "video" ? (
              <LessonCompleteButton lessonId={lesson.id} />
            ) : (
              <span />
            )}
            {lesson.next_lesson_id && (
              <Link href={lessonHref(lesson.next_lesson_id)} className={buttonVariants({ variant: "ghost" })}>
                {t("lesson.next")}
                <ArrowRight aria-hidden="true" />
              </Link>
            )}
          </div>

          <section aria-labelledby="ask-ai" className="flex flex-col gap-3">
            <div>
              <h2 id="ask-ai" className="flex items-center gap-2 text-lg font-bold">
                <Sparkles className="size-5 text-accent" aria-hidden="true" />
                {t("ai.lessonTitle")}
              </h2>
              <p className="text-sm text-muted-foreground">{t("ai.lessonHint")}</p>
            </div>
            <AIChat lessonId={lesson.id} compact />
          </section>

          <nav className="mt-2 flex flex-wrap justify-between gap-3 border-t border-border pt-5">
            {lesson.prev_lesson_id ? (
              <Link href={lessonHref(lesson.prev_lesson_id)} className={buttonVariants({ variant: "outline" })}>
                <ArrowLeft aria-hidden="true" />
                {t("lesson.prev")}
              </Link>
            ) : (
              <Link href={`/courses/${lesson.course.slug}`} className={buttonVariants({ variant: "ghost" })}>
                <ArrowLeft aria-hidden="true" />
                {t("lesson.backToCourse")}
              </Link>
            )}
            {lesson.next_lesson_id && (
              <Link href={lessonHref(lesson.next_lesson_id)} className={buttonVariants()}>
                {t("lesson.next")}
                <ArrowRight aria-hidden="true" />
              </Link>
            )}
          </nav>
          {lesson.course.is_demo && <p className="text-xs text-muted-foreground">{t("lesson.demoNotice")}</p>}
        </div>

        <aside aria-labelledby="outline" className="h-fit rounded-2xl border border-border bg-card lg:sticky lg:top-20">
          <h2 id="outline" className="border-b border-border px-5 py-4 font-semibold">
            {t("lesson.courseContent")}
          </h2>
          <LessonOutlineNav modules={lesson.modules} currentLessonId={lesson.id} courseSlug={lesson.course.slug} />
        </aside>
      </div>
    </CourseProgressProvider>
  );
}
