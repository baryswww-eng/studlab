import type { ReactNode } from "react";

/** Centered card layout shared by login / register pages. */
export function AuthShell({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string;
  subtitle: string;
  children: ReactNode;
  footer: ReactNode;
}) {
  return (
    <div className="relative isolate flex flex-1 items-center justify-center px-4 py-14">
      <div
        aria-hidden="true"
        className="pointer-events-none absolute left-1/2 top-10 -z-10 h-72 w-[40rem] -translate-x-1/2 rounded-full bg-gradient-to-r from-primary/25 to-accent/15 blur-3xl"
      />
      <div className="w-full max-w-md rounded-2xl border border-border bg-card p-6 shadow-2xl shadow-black/30 sm:p-8">
        <h1 className="text-2xl font-bold tracking-tight">{title}</h1>
        <p className="mt-1.5 text-sm text-muted-foreground">{subtitle}</p>
        <div className="mt-7">{children}</div>
        <p className="mt-6 text-center text-sm text-muted-foreground">{footer}</p>
      </div>
    </div>
  );
}
