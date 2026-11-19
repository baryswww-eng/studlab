"use client";

import { ArrowRight, BookCheck, Bot, Clock, Flame, GraduationCap, Trophy } from "lucide-react";
import { useTranslations } from "next-intl";
import { buttonVariants } from "@/components/ui/button";
import { EmptyState, ErrorState, Skeleton } from "@/components/ui/states";
import { useAuth } from "@/features/auth/auth-provider";
import { Link } from "@/i18n/navigation";
import { CabinetHeader } from "./cabinet-shell";
import { CourseProgressCard } from "./course-progress-card";
import { useDashboard } from "./use-dashboard";

export function NoCoursesYet() {
  const t = useTranslations("cabinet");
  return (
    <EmptyState
      title={t("emptyTitle")}
      text={t("emptyText")}
      action={
        <Link href="/courses" className={buttonVariants()}>
          {t("toCatalog")}
          <ArrowRight aria-hidden="true" />
        </Link>
      }
    />
  );
}

export function DashboardView() {
  const t = useTranslations("cabinet");
  const { user } = useAuth();
  const state = useDashboard();

  const firstName = user?.full_name.split(" ")[0] ?? "";

  return (
    <>
      <CabinetHeader title={t("greeting", { name: firstName })} text={t("greetingText")} />

      {state.status === "loading" && (
        <div className="grid gap-4 sm:grid-cols-3" aria-busy="true">
          {[0, 1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-24 rounded-2xl" />
          ))}
        </div>
      )}
      {state.status === "error" && <ErrorState text={t("loadError")} />}

      {state.status === "ready" && (
        <div className="flex flex-col gap-8">
          <dl className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {(
              [
                ["lessons", state.data.stats.lessons_completed, BookCheck, "text-success"],
                ["minutes", state.data.stats.minutes_learned, Clock, "text-accent"],
                ["streak", state.data.stats.streak_days, Flame, "text-warning"],
                ["courses", state.data.stats.courses_started, GraduationCap, "text-[#a996ff]"],
                ["completedCourses", state.data.stats.courses_completed, Trophy, "text-warning"],
                ["ai", state.data.stats.ai_questions, Bot, "text-accent"],
              ] as const
            ).map(([key, value, Icon, color]) => (
              <div key={key} className="flex items-center gap-4 rounded-2xl border border-border bg-card p-5">
                <span className="flex size-11 items-center justify-center rounded-xl bg-secondary">
                  <Icon className={`size-5 ${color}`} aria-hidden="true" />
                </span>
                <div className="flex flex-col">
                  <dt className="order-2 text-sm text-muted-foreground">{t(`stats.${key}`)}</dt>
                  <dd className="order-1 text-2xl font-extrabold">{value}</dd>
                </div>
              </div>
            ))}
          </dl>

          {state.data.courses.length === 0 ? (
            <NoCoursesYet />
          ) : (
            <>
              <section aria-labelledby="continue">
                <h2 id="continue" className="mb-3 text-lg font-bold">
                  {t("continueTitle")}
                </h2>
                <CourseProgressCard course={state.data.courses[0]} />
              </section>
              {state.data.courses.length > 1 && (
                <section aria-labelledby="my-courses">
                  <div className="mb-3 flex items-center justify-between gap-2">
                    <h2 id="my-courses" className="text-lg font-bold">
                      {t("myCoursesTitle")}
                    </h2>
                    <Link href="/my-courses" className={buttonVariants({ variant: "ghost", size: "sm" })}>
                      {t("allCourses")}
                      <ArrowRight aria-hidden="true" />
                    </Link>
                  </div>
                  <div className="grid gap-4 lg:grid-cols-2">
                    {state.data.courses.slice(1, 5).map((c) => (
                      <CourseProgressCard key={c.id} course={c} />
                    ))}
                  </div>
                </section>
              )}
            </>
          )}
        </div>
      )}
    </>
  );
}

export function MyCoursesView() {
  const t = useTranslations("cabinet");
  const state = useDashboard();
  return (
    <>
      <CabinetHeader title={t("myCoursesTitle")} text={t("myCoursesText")} />
      {state.status === "loading" && <Skeleton className="h-48 w-full rounded-2xl" />}
      {state.status === "error" && <ErrorState text={t("loadError")} />}
      {state.status === "ready" &&
        (state.data.courses.length === 0 ? (
          <NoCoursesYet />
        ) : (
          <div className="grid gap-4 lg:grid-cols-2">
            {state.data.courses.map((c) => (
              <CourseProgressCard key={c.id} course={c} />
            ))}
          </div>
        ))}
    </>
  );
}
