export type Role = "student" | "instructor" | "admin";

/** Response of GET /api/v1/users/me and POST /api/v1/auth/session */
export interface CurrentUser {
  id: number;
  email: string;
  full_name: string;
  role: Role;
  created_at: string;
}
