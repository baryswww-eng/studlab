"use client";

import { ArrowRight, CheckCircle2 } from "lucide-react";
import { useFormatter, useTranslations } from "next-intl";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { CategoryIcon, categoryGradient } from "@/features/courses/category-icon";
import { Link } from "@/i18n/navigation";
import { cn } from "@/lib/utils";
import type { DashboardCourse } from "@/services/me";

export function ProgressBar({ percent, label }: { percent: number; label: string }) {
  return (
    <div
      role="progressbar"
      aria-label={label}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={percent}
      className="h-2 overflow-hidden rounded-full bg-secondary"
    >
      <div
        className={cn("h-full rounded-full bg-gradient-to-r", percent === 100 ? "from-success to-success" : "from-primary to-accent")}
        style={{ width: `${percent}%` }}
      />
    </div>
  );
}

export function CourseProgressCard({ course }: { course: DashboardCourse }) {
  const t = useTranslations();
  const format = useFormatter();
  const finished = course.next_lesson_id === null;
  const progressText = t("progress.courseProgress", {
    completed: course.completed,
    total: course.total,
    percent: course.percent,
  });

  return (
    <article className="flex flex-col gap-4 rounded-2xl border border-border bg-card p-5">
      <div className="flex items-start gap-4">
        <span
          aria-hidden="true"
          className={cn(
            "flex size-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br text-white",
            categoryGradient(course.category_icon ?? undefined),
          )}
        >
          <CategoryIcon icon={course.category_icon ?? ""} className="size-6" />
        </span>
        <div className="min-w-0 flex-1">
          <h3 className="font-semibold leading-snug">
            <Link href={`/courses/${course.slug}`} className="hover:text-accent">
              {course.title}
            </Link>
          </h3>
          <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
            <Badge variant="outline">{t(`common.level.${course.level}`)}</Badge>
            <span>
              {t("cabinet.lastActivity", {
                date: format.relativeTime(new Date(course.last_activity_at)),
              })}
            </span>
          </div>
        </div>
      </div>
      <div className="flex flex-col gap-2">
        <p className="text-sm text-muted-foreground">{progressText}</p>
        <ProgressBar percent={course.percent} label={progressText} />
      </div>
      {finished ? (
        <div className="flex flex-wrap items-center justify-between gap-2">
          <p className="inline-flex items-center gap-1.5 text-sm font-semibold text-success">
            <CheckCircle2 className="size-4" aria-hidden="true" />
            {t("cabinet.courseDone")}
          </p>
          <Link href={`/courses/${course.slug}`} className={buttonVariants({ variant: "outline", size: "sm" })}>
            {t("cabinet.review")}
          </Link>
        </div>
      ) : (
        <div className="flex flex-wrap items-center justify-between gap-2">
          <p className="min-w-0 truncate text-sm text-muted-foreground">
            {t("cabinet.nextLesson", { title: course.next_lesson_title ?? "" })}
          </p>
          <Link
            href={`/courses/${course.slug}/lessons/${course.next_lesson_id}`}
            className={buttonVariants({ size: "sm" })}
          >
            {t("cabinet.continueButton")}
            <ArrowRight aria-hidden="true" />
          </Link>
        </div>
      )}
    </article>
  );
}
