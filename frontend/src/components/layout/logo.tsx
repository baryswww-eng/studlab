import { cn } from "@/lib/utils";

/** STUD LAB mark: a flask-shaped bracket in the brand gradient. */
export function Logo({ className }: { className?: string }) {
  return (
    <span className={cn("inline-flex items-center gap-2.5", className)}>
      <svg viewBox="0 0 32 32" aria-hidden="true" className="size-8 shrink-0">
        <defs>
          <linearGradient id="studlab-g" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0" stopColor="#7856FF" />
            <stop offset="1" stopColor="#38BDF8" />
          </linearGradient>
        </defs>
        <rect width="32" height="32" rx="9" fill="url(#studlab-g)" />
        <path
          d="M12.5 8v6.2L8.6 21.4A2.4 2.4 0 0 0 10.7 25h10.6a2.4 2.4 0 0 0 2.1-3.6l-3.9-7.2V8"
          fill="none"
          stroke="#F8FAFC"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <path d="M11 8h10M11.2 19h9.6" stroke="#F8FAFC" strokeWidth="2" strokeLinecap="round" />
      </svg>
      <span className="text-lg font-extrabold tracking-tight">
        STUD <span className="text-accent">LAB</span>
      </span>
    </span>
  );
}
