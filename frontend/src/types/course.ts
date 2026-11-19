import type { Locale } from "@/i18n/routing";

export type CourseLevel = "beginner" | "intermediate" | "advanced";
export type LessonType = "text" | "video" | "quiz" | "assignment";
export type CourseSort = "newest" | "title" | "price_asc" | "price_desc";
export type PriceFilter = "free" | "paid";

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface Category {
  id: number;
  slug: string;
  name: string;
  icon: string;
  course_count: number;
}

export interface CategorySummary {
  slug: string;
  name: string;
  icon: string;
}

export interface InstructorSummary {
  id: number;
  full_name: string;
  headline: string | null;
}

export interface Instructor extends InstructorSummary {
  bio: string | null;
  avatar_url: string | null;
}

export interface CourseCard {
  id: number;
  slug: string;
  locale: Locale;
  title: string;
  short_description: string;
  level: CourseLevel;
  /** Decimal serialized as string, e.g. "9900.00" */
  price: string;
  currency: string;
  is_free: boolean;
  cover_url: string | null;
  category: CategorySummary | null;
  instructor: InstructorSummary;
  lessons_count: number;
  duration_minutes: number;
  is_featured: boolean;
  is_demo: boolean;
}

export interface LessonOutline {
  id: number;
  position: number;
  title: string;
  type: LessonType;
  duration_minutes: number;
  is_preview: boolean;
  has_video: boolean;
}

export interface LessonDetail {
  id: number;
  title: string;
  type: LessonType;
  duration_minutes: number;
  module_position: number;
  module_title: string;
  content_md: string;
  youtube_id: string | null;
  video_author: string | null;
  course: { id: number; slug: string; title: string; is_demo: boolean };
  modules: ModuleOutline[];
  prev_lesson_id: number | null;
  next_lesson_id: number | null;
}

export interface ModuleOutline {
  id: number;
  position: number;
  title: string;
  lessons: LessonOutline[];
}

export interface CourseDetail extends Omit<CourseCard, "instructor"> {
  description: string;
  outcomes: string[];
  requirements: string[];
  instructor: Instructor;
  modules: ModuleOutline[];
  published_at: string | null;
}

export interface PublicStats {
  published_courses: number;
  categories: number;
  lessons: number;
}

export interface CourseQuery {
  q?: string;
  category?: string;
  level?: CourseLevel;
  price?: PriceFilter;
  sort?: CourseSort;
  featured?: boolean;
  page?: number;
  page_size?: number;
}
