import { apiFetch } from "@/lib/api";

export type QuestionType = "single" | "multiple" | "text";

export interface QuizQuestion {
  id: number;
  position: number;
  type: QuestionType;
  text: string;
  points: number;
  options: { id: number; text: string }[];
}

export interface QuestionResult {
  question_id: number;
  correct: boolean;
  points_earned: number;
  correct_option_ids: number[];
  accepted_answers: string[];
  explanation: string;
}

export interface AttemptResult {
  attempt_id: number;
  score: number;
  max_score: number;
  percent: number;
  passed: boolean;
  results: QuestionResult[];
  created_at: string;
}

export interface Quiz {
  id: number;
  lesson_id: number;
  pass_percent: number;
  questions: QuizQuestion[];
  last_attempt: AttemptResult | null;
  attempts_count: number;
}

export type QuizAnswers = Record<number, number[] | string>;

export interface Submission {
  id: number;
  status: "submitted" | "accepted" | "needs_work";
  content: string;
  score: number | null;
  feedback_md: string | null;
  reviewed_by: string | null;
  created_at: string;
}

export interface Assignment {
  id: number;
  lesson_id: number;
  description_md: string;
  expected_md: string;
  answer_format: "code" | "text";
  submissions: Submission[];
}

const NO_STORE = { cache: "no-store" } as const;

export function getQuiz(lessonId: number) {
  return apiFetch<Quiz>(`/quizzes/by-lesson/${lessonId}`, NO_STORE);
}

export function submitQuiz(quizId: number, answers: QuizAnswers) {
  return apiFetch<AttemptResult>(`/quizzes/${quizId}/submit`, { method: "POST", body: { answers } });
}

export function getAssignment(lessonId: number) {
  return apiFetch<Assignment>(`/assignments/by-lesson/${lessonId}`, NO_STORE);
}

export function submitAssignment(assignmentId: number, content: string) {
  return apiFetch<Submission>(`/assignments/${assignmentId}/submissions`, {
    method: "POST",
    body: { content },
    timeoutMs: 120_000, // AI review can take a while
  });
}
