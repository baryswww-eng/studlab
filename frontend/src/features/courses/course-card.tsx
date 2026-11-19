import { BookOpen, Clock, UserRound } from "lucide-react";
import { useFormatter, useTranslations } from "next-intl";
import { Badge } from "@/components/ui/badge";
import { Link } from "@/i18n/navigation";
import type { CourseCard as CourseCardData } from "@/types/course";
import { CourseCover } from "./category-icon";
import { durationParts, formatPrice } from "./format";

export function CourseCard({ course }: { course: CourseCardData }) {
  const t = useTranslations();
  const format = useFormatter();

  return (
    <article className="group relative flex flex-col overflow-hidden rounded-2xl border border-border bg-card transition-all hover:-translate-y-0.5 hover:border-primary/50 hover:shadow-xl hover:shadow-primary/10">
      <div className="relative">
        <CourseCover icon={course.category?.icon} title={course.title} coverUrl={course.cover_url} />
        <div className="absolute left-3 top-3 flex gap-1.5">
          {course.is_demo && <Badge variant="warning">{t("common.demo")}</Badge>}
        </div>
      </div>
      <div className="flex flex-1 flex-col gap-3 p-5">
        <div className="flex flex-wrap items-center gap-2">
          {course.category && <Badge variant="accent">{course.category.name}</Badge>}
          <Badge variant="outline">{t(`common.level.${course.level}`)}</Badge>
        </div>
        <h3 className="text-lg font-semibold leading-snug">
          {/* The whole card is clickable via the stretched link. */}
          <Link
            href={`/courses/${course.slug}`}
            className="after:absolute after:inset-0 focus-visible:outline-none group-focus-within:text-accent"
          >
            {course.title}
          </Link>
        </h3>
        <p className="line-clamp-2 text-sm text-muted-foreground">{course.short_description}</p>
        <p className="inline-flex items-center gap-1.5 text-sm text-muted-foreground">
          <UserRound className="size-4" aria-hidden="true" />
          {course.instructor.full_name}
        </p>
        <div className="mt-auto flex items-center justify-between gap-3 border-t border-border pt-4 text-sm">
          <div className="flex items-center gap-3 text-muted-foreground">
            <span className="inline-flex items-center gap-1">
              <BookOpen className="size-4" aria-hidden="true" />
              {t("common.lessons", { count: course.lessons_count })}
            </span>
            <span className="inline-flex items-center gap-1">
              <Clock className="size-4" aria-hidden="true" />
              {t("common.duration", durationParts(course.duration_minutes))}
            </span>
          </div>
          <span className={course.is_free ? "font-semibold text-success" : "font-semibold"}>
            {formatPrice(format, course, t("common.free"))}
          </span>
        </div>
      </div>
    </article>
  );
}
