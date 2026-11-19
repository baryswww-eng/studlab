"use client";

import { BookOpen, LayoutDashboard, Settings, UserRound } from "lucide-react";
import { useTranslations } from "next-intl";
import { type ReactNode, useEffect } from "react";
import { Skeleton } from "@/components/ui/states";
import { useAuth } from "@/features/auth/auth-provider";
import { Link, usePathname, useRouter } from "@/i18n/navigation";
import { cn } from "@/lib/utils";

const ITEMS = [
  { href: "/dashboard", key: "dashboard", icon: LayoutDashboard },
  { href: "/my-courses", key: "myCourses", icon: BookOpen },
  { href: "/profile", key: "profile", icon: UserRound },
  { href: "/settings", key: "settings", icon: Settings },
] as const;

/**
 * Layout for the student cabinet. Guests are sent to /login?next=… (UX only —
 * every cabinet API call is authorized on the backend).
 */
export function CabinetShell({ children }: { children: ReactNode }) {
  const t = useTranslations("cabinet");
  const { user, loading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.replace({ pathname: "/login", query: { next: pathname } });
  }, [loading, user, pathname, router]);

  return (
    <div className="mx-auto grid w-full max-w-6xl gap-8 px-4 py-8 sm:px-6 md:grid-cols-[220px_1fr]">
      <nav aria-label={t("navLabel")} className="h-fit md:sticky md:top-20">
        <ul className="flex gap-1 overflow-x-auto md:flex-col">
          {ITEMS.map(({ href, key, icon: Icon }) => {
            const active = pathname === href;
            return (
              <li key={href} className="shrink-0">
                <Link
                  href={href}
                  aria-current={active ? "page" : undefined}
                  className={cn(
                    "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                    active ? "bg-primary/15 text-foreground" : "text-muted-foreground hover:bg-secondary hover:text-foreground",
                  )}
                >
                  <Icon className={cn("size-4", active && "text-accent")} aria-hidden="true" />
                  {t(`nav.${key}`)}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
      <div className="min-w-0">
        {loading || !user ? (
          <div className="flex flex-col gap-4" aria-busy="true">
            <Skeleton className="h-10 w-72" />
            <Skeleton className="h-32 w-full rounded-2xl" />
            <Skeleton className="h-64 w-full rounded-2xl" />
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  );
}

export function CabinetHeader({ title, text }: { title: string; text?: string }) {
  return (
    <header className="mb-6">
      <h1 className="text-2xl font-extrabold tracking-tight sm:text-3xl">{title}</h1>
      {text && <p className="mt-1 text-muted-foreground">{text}</p>}
    </header>
  );
}
