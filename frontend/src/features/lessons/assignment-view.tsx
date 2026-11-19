"use client";

import { Bot, CheckCircle2, Clock, Loader2, Send, Wrench } from "lucide-react";
import { useFormatter, useTranslations } from "next-intl";
import { useEffect, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { ErrorState, Skeleton } from "@/components/ui/states";
import { Markdown } from "@/features/ai/markdown";
import { useAuth } from "@/features/auth/auth-provider";
import { Link, usePathname } from "@/i18n/navigation";
import { cn } from "@/lib/utils";
import { type Assignment, getAssignment, type Submission, submitAssignment } from "@/services/assessment";

const STATUS_STYLE = {
  accepted: { variant: "success", icon: CheckCircle2 },
  needs_work: { variant: "warning", icon: Wrench },
  submitted: { variant: "outline", icon: Clock },
} as const;

function SubmissionCard({ submission }: { submission: Submission }) {
  const t = useTranslations("assignment");
  const format = useFormatter();
  const style = STATUS_STYLE[submission.status];
  const Icon = style.icon;
  return (
    <article className="flex flex-col gap-3 rounded-2xl border border-border bg-card p-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <Badge variant={style.variant}>
            <Icon className="size-3.5" aria-hidden="true" />
            {t(`status.${submission.status}`)}
          </Badge>
          {submission.score !== null && (
            <span className="text-sm font-semibold">{t("score", { score: submission.score })}</span>
          )}
        </div>
        <span className="text-xs text-muted-foreground">
          {format.relativeTime(new Date(submission.created_at))}
          {submission.reviewed_by && ` · ${submission.reviewed_by}`}
        </span>
      </div>
      {submission.feedback_md ? (
        <div className="flex gap-3">
          <span className="flex size-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-primary to-accent text-white">
            <Bot className="size-4" aria-hidden="true" />
          </span>
          <div className="min-w-0 flex-1">
            <Markdown>{submission.feedback_md}</Markdown>
          </div>
        </div>
      ) : (
        submission.status === "submitted" && <p className="text-sm text-muted-foreground">{t("waiting")}</p>
      )}
      <details className="text-sm">
        <summary className="cursor-pointer text-muted-foreground hover:text-foreground">{t("yourSolution")}</summary>
        <pre className="mt-2 max-h-64 overflow-auto rounded-xl border border-border bg-[#0b111e] p-3 font-mono text-xs">
          {submission.content}
        </pre>
      </details>
    </article>
  );
}

export function AssignmentView({ lessonId, onAccepted }: { lessonId: number; onAccepted?: () => void }) {
  const t = useTranslations("assignment");
  const { user } = useAuth();
  const pathname = usePathname();
  const [assignment, setAssignment] = useState<Assignment | null>(null);
  const [failed, setFailed] = useState(false);
  const [content, setContent] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getAssignment(lessonId)
      .then((a) => !cancelled && setAssignment(a))
      .catch(() => !cancelled && setFailed(true));
    return () => {
      cancelled = true;
    };
  }, [lessonId, user]);

  if (failed) return <ErrorState text={t("loadError")} />;
  if (!assignment) return <Skeleton className="h-96 w-full rounded-2xl" />;

  const isCode = assignment.answer_format === "code";

  async function onSubmit() {
    if (!assignment || !content.trim()) return;
    setPending(true);
    setError(null);
    try {
      const s = await submitAssignment(assignment.id, content);
      setAssignment({ ...assignment, submissions: [s, ...assignment.submissions] });
      if (s.status === "accepted") onAccepted?.();
    } catch {
      setError(t("error"));
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="flex flex-col gap-5">
      <section className="rounded-2xl border border-border bg-card p-5">
        <h2 className="mb-2 text-lg font-bold">{t("task")}</h2>
        <Markdown>{assignment.description_md}</Markdown>
        {assignment.expected_md && (
          <>
            <h3 className="mb-1 mt-4 font-semibold">{t("expected")}</h3>
            <Markdown>{assignment.expected_md}</Markdown>
          </>
        )}
      </section>

      <section className="flex flex-col gap-3">
        <label htmlFor={`solution-${lessonId}`} className="font-semibold">
          {t("yourSolution")}
        </label>
        <textarea
          id={`solution-${lessonId}`}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          maxLength={20000}
          rows={isCode ? 14 : 8}
          spellCheck={!isCode}
          disabled={!user || pending}
          placeholder={isCode ? t("codePlaceholder") : t("textPlaceholder")}
          className={cn(
            "w-full resize-y rounded-xl border border-input bg-[#0b111e] p-4 text-sm text-foreground placeholder:text-muted-foreground/70",
            "focus-visible:border-ring focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/30 disabled:opacity-60",
            isCode && "font-mono leading-6",
          )}
          onKeyDown={(e) => {
            // Tab inserts spaces in code instead of leaving the field.
            if (isCode && e.key === "Tab" && !e.shiftKey) {
              e.preventDefault();
              const el = e.currentTarget;
              const { selectionStart: s, selectionEnd: end } = el;
              const next = `${content.slice(0, s)}    ${content.slice(end)}`;
              setContent(next);
              requestAnimationFrame(() => el.setSelectionRange(s + 4, s + 4));
            }
          }}
        />
        <p className="text-xs text-muted-foreground">{t("hint")}</p>
        {error && (
          <p role="alert" className="text-sm text-warning">
            {error}
          </p>
        )}
        {user ? (
          <Button size="lg" className="w-full sm:w-fit" disabled={pending || !content.trim()} onClick={onSubmit}>
            {pending ? <Loader2 className="animate-spin" aria-hidden="true" /> : <Send aria-hidden="true" />}
            {pending ? t("submitting") : t("submit")}
          </Button>
        ) : (
          <Link href={{ pathname: "/login", query: { next: pathname } }} className={buttonVariants({ size: "lg" })}>
            {t("loginToSubmit")}
          </Link>
        )}
      </section>

      {assignment.submissions.length > 0 && (
        <section className="flex flex-col gap-3" aria-live="polite">
          <h2 className="text-lg font-bold">{t("history")}</h2>
          {assignment.submissions.map((s) => (
            <SubmissionCard key={s.id} submission={s} />
          ))}
        </section>
      )}
    </div>
  );
}
