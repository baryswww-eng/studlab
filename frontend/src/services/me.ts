import { ApiError, apiFetch } from "@/lib/api";
import type { CourseLevel } from "@/types/course";
import type { CurrentUser } from "@/types/user";

export interface CourseProgress {
  course_id: number;
  completed_lesson_ids: number[];
  completed: number;
  total: number;
  percent: number;
}

export interface DashboardCourse {
  id: number;
  slug: string;
  title: string;
  category_icon: string | null;
  level: CourseLevel;
  completed: number;
  total: number;
  percent: number;
  last_activity_at: string;
  next_lesson_id: number | null;
  next_lesson_title: string | null;
}

export interface Dashboard {
  stats: {
    courses_started: number;
    courses_completed: number;
    lessons_completed: number;
    minutes_learned: number;
    streak_days: number;
    active_days_last_7: number;
    ai_questions: number;
  };
  courses: DashboardCourse[];
}

const NO_STORE = { cache: "no-store" } as const;

export function getCourseProgress(slug: string) {
  return apiFetch<CourseProgress>(`/progress/courses/${encodeURIComponent(slug)}`, NO_STORE);
}

export function setLessonCompleted(lessonId: number, completed: boolean) {
  return apiFetch<CourseProgress>(`/progress/lessons/${lessonId}`, {
    method: completed ? "PUT" : "DELETE",
  });
}

export function getDashboard() {
  return apiFetch<Dashboard>("/users/me/dashboard", NO_STORE);
}

export function updateProfile(fullName: string) {
  return apiFetch<CurrentUser>("/users/me", { method: "PATCH", body: { full_name: fullName } });
}

export type PasswordChangeResult = "ok" | "wrongPassword" | "samePassword" | "unknownError";

export async function changePassword(current: string, next: string): Promise<PasswordChangeResult> {
  try {
    await apiFetch("/users/me/password", {
      method: "POST",
      body: { current_password: current, new_password: next },
    });
    return "ok";
  } catch (error) {
    if (error instanceof ApiError && error.code === "wrong_password") return "wrongPassword";
    if (error instanceof ApiError && error.code === "same_password") return "samePassword";
    return "unknownError";
  }
}
