"use client";

import { Check, CheckCircle2, Circle, CircleHelp, FileText, Loader2, PlayCircle, SquarePen } from "lucide-react";
import { useTranslations } from "next-intl";
import { createContext, type ReactNode, use, useEffect, useState } from "react";
import { Button, buttonVariants } from "@/components/ui/button";
import { useAuth } from "@/features/auth/auth-provider";
import { durationParts } from "@/features/courses/format";
import { Link, usePathname } from "@/i18n/navigation";
import { cn } from "@/lib/utils";
import { type CourseProgress, getCourseProgress, setLessonCompleted } from "@/services/me";
import type { LessonType, ModuleOutline } from "@/types/course";

type State = {
  progress: CourseProgress | null;
  done: Set<number>;
  toggle: (lessonId: number, completed: boolean) => Promise<boolean>;
  refresh: () => void;
};

const Ctx = createContext<State | null>(null);

/** Loads the signed-in student's progress for a course (saved on the backend). */
export function CourseProgressProvider({ slug, children }: { slug: string; children: ReactNode }) {
  const { user } = useAuth();
  const [progress, setProgress] = useState<CourseProgress | null>(null);
  const [version, setVersion] = useState(0);

  useEffect(() => {
    if (!user) return;
    let cancelled = false;
    getCourseProgress(slug)
      .then((p) => !cancelled && setProgress(p))
      .catch(() => undefined);
    return () => {
      cancelled = true;
    };
  }, [slug, user, version]);

  async function toggle(lessonId: number, completed: boolean) {
    try {
      setProgress(await setLessonCompleted(lessonId, completed));
      return true;
    } catch {
      return false;
    }
  }

  const visible = user ? progress : null;
  const done = new Set(visible?.completed_lesson_ids ?? []);
  const refresh = () => setVersion((v) => v + 1);
  return <Ctx value={{ progress: visible, done, toggle, refresh }}>{children}</Ctx>;
}

export function useCourseProgress() {
  const ctx = use(Ctx);
  if (!ctx) throw new Error("useCourseProgress must be used inside <CourseProgressProvider>");
  return ctx;
}

/** "Mark as completed" for the current lesson. Guests get a sign-in link instead. */
export function LessonCompleteButton({ lessonId }: { lessonId: number }) {
  const t = useTranslations("progress");
  const { user, loading } = useAuth();
  const pathname = usePathname();
  const { done, toggle } = useCourseProgress();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState(false);
  const isDone = done.has(lessonId);

  if (loading) return null;
  if (!user) {
    return (
      <Link
        href={{ pathname: "/login", query: { next: pathname } }}
        className={buttonVariants({ variant: "outline" })}
      >
        <Circle aria-hidden="true" />
        {t("guestHint")}
      </Link>
    );
  }

  return (
    <div className="flex flex-col items-start gap-1">
      <Button
        variant={isDone ? "secondary" : "primary"}
        disabled={pending}
        aria-pressed={isDone}
        onClick={async () => {
          setPending(true);
          setError(false);
          const ok = await toggle(lessonId, !isDone);
          setError(!ok);
          setPending(false);
        }}
        className={cn(isDone && "text-success")}
        title={isDone ? t("undo") : undefined}
      >
        {pending ? <Loader2 className="animate-spin" aria-hidden="true" /> : isDone ? <CheckCircle2 aria-hidden="true" /> : <Check aria-hidden="true" />}
        {pending ? t("saving") : isDone ? t("done") : t("markDone")}
      </Button>
      {error && (
        <p role="alert" className="text-xs text-warning">
          {t("error")}
        </p>
      )}
    </div>
  );
}

const ICON: Record<LessonType, typeof FileText> = {
  text: FileText,
  video: PlayCircle,
  quiz: CircleHelp,
  assignment: SquarePen,
};

/** Course outline with completion checkmarks for signed-in students. */
export function LessonOutlineNav({
  modules,
  currentLessonId,
  courseSlug,
}: {
  modules: ModuleOutline[];
  currentLessonId: number;
  courseSlug: string;
}) {
  const t = useTranslations();
  const { progress, done } = useCourseProgress();

  return (
    <>
      {progress && (
        <div className="border-b border-border px-5 py-3">
          <p className="text-xs text-muted-foreground">
            {t("progress.courseProgress", {
              completed: progress.completed,
              total: progress.total,
              percent: progress.percent,
            })}
          </p>
          <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-secondary" aria-hidden="true">
            <div className="h-full rounded-full bg-gradient-to-r from-primary to-accent" style={{ width: `${progress.percent}%` }} />
          </div>
        </div>
      )}
      <ol className="max-h-[70vh] overflow-y-auto py-2">
        {modules.map((m) => (
          <li key={m.id}>
            <p className="px-5 pb-1 pt-3 text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              {m.position}. {m.title}
            </p>
            <ul>
              {m.lessons.map((l) => {
                const isDone = done.has(l.id);
                const Icon = isDone ? CheckCircle2 : ICON[l.type];
                const current = l.id === currentLessonId;
                return (
                  <li key={l.id}>
                    <Link
                      href={`/courses/${courseSlug}/lessons/${l.id}`}
                      aria-current={current ? "page" : undefined}
                      className={cn(
                        "flex items-center gap-3 px-5 py-2.5 text-sm transition-colors hover:bg-secondary/60",
                        current && "bg-primary/15 font-semibold text-foreground",
                      )}
                    >
                      <Icon
                        className={cn(
                          "size-4 shrink-0",
                          isDone ? "text-success" : l.has_video ? "text-accent" : "text-muted-foreground",
                        )}
                        aria-hidden="true"
                      />
                      <span className="min-w-0 flex-1">
                        {l.title}
                        {isDone && <span className="sr-only"> ({t("progress.completedLabel")})</span>}
                      </span>
                      <span className="shrink-0 text-xs text-muted-foreground">
                        {t("common.duration", durationParts(l.duration_minutes))}
                      </span>
                    </Link>
                  </li>
                );
              })}
            </ul>
          </li>
        ))}
      </ol>
    </>
  );
}
