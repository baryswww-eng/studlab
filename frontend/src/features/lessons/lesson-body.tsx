"use client";

import { Markdown } from "@/features/ai/markdown";
import { useCourseProgress } from "@/features/progress/course-progress";
import type { LessonType } from "@/types/course";
import { AssignmentView } from "./assignment-view";
import { QuizView } from "./quiz-view";

/** Theory article, quiz or practical task. Video lessons are rendered by the page itself. */
export function LessonBody({ lessonId, type, content }: { lessonId: number; type: LessonType; content: string }) {
  const { refresh } = useCourseProgress();

  if (type === "quiz") return <QuizView lessonId={lessonId} onPassed={refresh} />;
  if (type === "assignment") return <AssignmentView lessonId={lessonId} onAccepted={refresh} />;
  return (
    <article className="rounded-2xl border border-border bg-card p-6 sm:p-8 [&_.ai-markdown]:text-[15px] [&_.ai-markdown]:leading-7 [&_h3]:text-xl">
      <Markdown>{content}</Markdown>
    </article>
  );
}
