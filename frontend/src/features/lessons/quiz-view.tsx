"use client";

import { CheckCircle2, Loader2, RotateCcw, Trophy, XCircle } from "lucide-react";
import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";
import { Button, buttonVariants } from "@/components/ui/button";
import { Input } from "@/components/ui/form-controls";
import { ErrorState, Skeleton } from "@/components/ui/states";
import { Markdown } from "@/features/ai/markdown";
import { useAuth } from "@/features/auth/auth-provider";
import { Link, usePathname } from "@/i18n/navigation";
import { cn } from "@/lib/utils";
import { type AttemptResult, getQuiz, type Quiz, type QuizAnswers, submitQuiz } from "@/services/assessment";

export function QuizView({ lessonId, onPassed }: { lessonId: number; onPassed?: () => void }) {
  const t = useTranslations("quiz");
  const { user } = useAuth();
  const pathname = usePathname();
  const [quiz, setQuiz] = useState<Quiz | null>(null);
  const [failed, setFailed] = useState(false);
  const [answers, setAnswers] = useState<QuizAnswers>({});
  const [result, setResult] = useState<AttemptResult | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    getQuiz(lessonId)
      .then((q) => {
        if (cancelled) return;
        setQuiz(q);
        if (q.last_attempt) setResult(q.last_attempt);
      })
      .catch(() => !cancelled && setFailed(true));
    return () => {
      cancelled = true;
    };
  }, [lessonId, user]);

  if (failed) return <ErrorState text={t("loadError")} />;
  if (!quiz) return <Skeleton className="h-96 w-full rounded-2xl" />;

  const answered = quiz.questions.filter((q) => {
    const a = answers[q.id];
    return Array.isArray(a) ? a.length > 0 : typeof a === "string" && a.trim() !== "";
  }).length;
  const left = quiz.questions.length - answered;
  const resultFor = (id: number) => result?.results.find((r) => r.question_id === id);

  function choose(questionId: number, optionId: number, multiple: boolean) {
    if (result) return;
    setAnswers((prev) => {
      const current = (prev[questionId] as number[] | undefined) ?? [];
      const next = multiple
        ? current.includes(optionId)
          ? current.filter((x) => x !== optionId)
          : [...current, optionId]
        : [optionId];
      return { ...prev, [questionId]: next };
    });
  }

  async function onSubmit() {
    if (!quiz) return;
    if (left > 0) {
      setError(t("unanswered", { left }));
      return;
    }
    setPending(true);
    setError(null);
    try {
      const r = await submitQuiz(quiz.id, answers);
      setResult(r);
      setQuiz({ ...quiz, attempts_count: quiz.attempts_count + 1 });
      if (r.passed) onPassed?.();
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch {
      setError(t("error"));
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="flex flex-col gap-5">
      <p className="text-sm text-muted-foreground">
        {t("intro", { count: quiz.questions.length, percent: quiz.pass_percent })}
        {quiz.attempts_count > 0 && <> · {t("attempts", { count: quiz.attempts_count })}</>}
      </p>

      {result && (
        <div
          role="status"
          className={cn(
            "flex flex-wrap items-center justify-between gap-3 rounded-2xl border p-5",
            result.passed ? "border-success/40 bg-success/10" : "border-warning/40 bg-warning/10",
          )}
        >
          <div className="flex items-center gap-3">
            {result.passed ? (
              <Trophy className="size-8 text-success" aria-hidden="true" />
            ) : (
              <XCircle className="size-8 text-warning" aria-hidden="true" />
            )}
            <div>
              <p className="text-lg font-bold">{result.passed ? t("passed") : t("failed")}</p>
              <p className="text-sm text-muted-foreground">
                {t("score", { score: result.score, max: result.max_score, percent: result.percent })}
              </p>
            </div>
          </div>
          <Button
            variant="outline"
            onClick={() => {
              setResult(null);
              setAnswers({});
            }}
          >
            <RotateCcw aria-hidden="true" />
            {t("retry")}
          </Button>
        </div>
      )}

      <ol className="flex flex-col gap-4">
        {quiz.questions.map((q, index) => {
          const r = resultFor(q.id);
          const selected = (answers[q.id] as number[] | undefined) ?? [];
          return (
            <li
              key={q.id}
              className={cn(
                "rounded-2xl border bg-card p-5",
                r ? (r.correct ? "border-success/50" : "border-destructive/50") : "border-border",
              )}
            >
              <fieldset disabled={Boolean(result) || pending}>
                <legend className="mb-1 flex w-full items-start justify-between gap-3">
                  <span className="font-semibold">
                    {index + 1}. <InlineMarkdown text={q.text} />
                  </span>
                  {r && (
                    <span
                      className={cn(
                        "inline-flex shrink-0 items-center gap-1 text-sm font-semibold",
                        r.correct ? "text-success" : "text-destructive",
                      )}
                    >
                      {r.correct ? <CheckCircle2 className="size-4" /> : <XCircle className="size-4" />}
                      {r.correct ? t("correct") : t("wrong")}
                    </span>
                  )}
                </legend>
                <p className="mb-3 text-xs text-muted-foreground">{t(q.type)}</p>

                {q.type === "text" ? (
                  <Input
                    aria-label={t("text")}
                    placeholder={t("textPlaceholder")}
                    maxLength={200}
                    value={(answers[q.id] as string | undefined) ?? ""}
                    onChange={(e) => setAnswers((prev) => ({ ...prev, [q.id]: e.target.value }))}
                  />
                ) : (
                  <div className="flex flex-col gap-2">
                    {q.options.map((o) => {
                      const isSelected = selected.includes(o.id);
                      const isRight = r?.correct_option_ids.includes(o.id);
                      return (
                        <label
                          key={o.id}
                          className={cn(
                            "flex cursor-pointer items-center gap-3 rounded-xl border px-4 py-3 text-sm transition-colors",
                            isSelected ? "border-primary bg-primary/10" : "border-border hover:bg-secondary/50",
                            r && isSelected && !isRight && "border-destructive bg-destructive/10",
                            r && isRight && "border-success bg-success/10",
                          )}
                        >
                          <input
                            type={q.type === "single" ? "radio" : "checkbox"}
                            name={`q-${q.id}`}
                            checked={isSelected}
                            onChange={() => choose(q.id, o.id, q.type === "multiple")}
                            className="size-4 accent-[#7856FF]"
                          />
                          <InlineMarkdown text={o.text} />
                        </label>
                      );
                    })}
                  </div>
                )}

                {r && (
                  <div className="mt-3 rounded-xl bg-secondary/50 p-3 text-sm">
                    {!r.correct && r.accepted_answers.length > 0 && (
                      <p className="mb-1 font-medium">{t("correctAnswer", { answer: r.accepted_answers[0] })}</p>
                    )}
                    <InlineMarkdown text={r.explanation} />
                  </div>
                )}
              </fieldset>
            </li>
          );
        })}
      </ol>

      {!result &&
        (user ? (
          <div className="flex flex-col gap-2">
            {error && (
              <p role="alert" className="text-sm text-warning">
                {error}
              </p>
            )}
            <Button size="lg" className="w-full sm:w-fit" disabled={pending} onClick={onSubmit}>
              {pending && <Loader2 className="animate-spin" aria-hidden="true" />}
              {pending ? t("submitting") : t("submit")}
            </Button>
          </div>
        ) : (
          <Link href={{ pathname: "/login", query: { next: pathname } }} className={buttonVariants({ size: "lg" })}>
            {t("loginToSubmit")}
          </Link>
        ))}
    </div>
  );
}

/** Inline code / bold in short question texts (no raw HTML). */
function InlineMarkdown({ text }: { text: string }) {
  return (
    <span className="[&_.ai-markdown]:inline [&_p]:my-0 [&_p]:inline">
      <Markdown>{text}</Markdown>
    </span>
  );
}
