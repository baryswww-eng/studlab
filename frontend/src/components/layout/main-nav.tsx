"use client";

import { LogOut, Menu, X } from "lucide-react";
import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";
import { buttonVariants } from "@/components/ui/button";
import { useAuth } from "@/features/auth/auth-provider";
import { Link, usePathname, useRouter } from "@/i18n/navigation";
import { mainNav } from "@/lib/site";
import { cn } from "@/lib/utils";

function isActive(pathname: string, href: string) {
  return href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);
}

/** Desktop navigation + mobile disclosure menu. */
export function MainNav() {
  const t = useTranslations();
  const pathname = usePathname();
  const router = useRouter();
  const { user, loading, logout } = useAuth();
  const [open, setOpen] = useState(false);

  // Close the mobile menu on Escape (links close it on click).
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  const links = mainNav.map(({ href, key }) => {
    const active = isActive(pathname, href);
    return (
      <Link
        key={href}
        href={href}
        aria-current={active ? "page" : undefined}
        onClick={() => setOpen(false)}
        className={cn(
          "rounded-lg px-3 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
          active ? "text-foreground" : "text-muted-foreground hover:text-foreground",
          active && "bg-secondary",
        )}
      >
        {t(`nav.${key}`)}
      </Link>
    );
  });

  const authButtons = loading ? (
    <span className="h-9 w-40 animate-pulse rounded-lg bg-secondary" aria-hidden="true" />
  ) : user ? (
    <>
      <Link href="/dashboard" onClick={() => setOpen(false)} className="flex items-center gap-2 rounded-lg px-2 py-1 text-sm transition-colors hover:bg-secondary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring" title={user.email}>
        <span
          aria-hidden="true"
          className="flex size-8 items-center justify-center rounded-full bg-gradient-to-br from-primary to-accent text-sm font-bold text-white"
        >
          {user.full_name.charAt(0).toUpperCase()}
        </span>
        <span className="max-w-36 truncate font-medium">{user.full_name}</span>
        <span className="sr-only"> — {t("nav.dashboard")}</span>
      </Link>
      <button
        type="button"
        onClick={async () => {
          setOpen(false);
          await logout();
          router.refresh();
        }}
        className={buttonVariants({ variant: "ghost", size: "sm" })}
      >
        <LogOut aria-hidden="true" />
        {t("auth.logout")}
      </button>
    </>
  ) : (
    <>
      <Link
        href="/login"
        onClick={() => setOpen(false)}
        className={buttonVariants({ variant: "ghost", size: "sm" })}
      >
        {t("nav.login")}
      </Link>
      <Link
        href="/register"
        onClick={() => setOpen(false)}
        className={buttonVariants({ variant: "primary", size: "sm" })}
      >
        {t("nav.register")}
      </Link>
    </>
  );

  return (
    <>
      <nav aria-label={t("a11y.mainNav")} className="hidden items-center gap-1 md:flex">
        {links}
      </nav>
      <div className="hidden items-center gap-2 md:flex">
        {authButtons}
      </div>

      <button
        type="button"
        className={cn(buttonVariants({ variant: "ghost", size: "icon" }), "md:hidden")}
        aria-expanded={open}
        aria-controls="mobile-menu"
        aria-label={open ? t("a11y.closeMenu") : t("a11y.openMenu")}
        onClick={() => setOpen((v) => !v)}
      >
        {open ? <X className="size-5" /> : <Menu className="size-5" />}
      </button>

      {open && (
        <div
          id="mobile-menu"
          className="absolute inset-x-0 top-16 border-b border-border bg-background shadow-2xl shadow-black/50 md:hidden"
        >
          <nav aria-label={t("a11y.mainNav")} className="mx-auto flex max-w-6xl flex-col gap-1 px-4 py-4">
            {links}
            <div className="mt-3 flex items-center justify-end gap-3 border-t border-border pt-4">
              <div className="flex gap-2">{authButtons}</div>
            </div>
          </nav>
        </div>
      )}
    </>
  );
}
