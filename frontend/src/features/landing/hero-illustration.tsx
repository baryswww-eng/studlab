import { CheckCircle2, Sparkles, Trophy } from "lucide-react";

/** Brand illustration: a code editor with floating progress chips (decorative). */
export function HeroIllustration() {
  return (
    <div aria-hidden="true" className="relative mx-auto w-full max-w-md select-none lg:max-w-none">
      <div className="absolute -inset-6 -z-10 rounded-[2rem] bg-gradient-to-br from-primary/30 via-accent/10 to-transparent blur-2xl" />
      <div className="overflow-hidden rounded-2xl border border-border bg-[#0c1322] shadow-2xl shadow-black/40">
        <div className="flex items-center gap-2 border-b border-border px-4 py-3">
          <span className="size-3 rounded-full bg-[#f87171]" />
          <span className="size-3 rounded-full bg-[#fbbf24]" />
          <span className="size-3 rounded-full bg-[#34d399]" />
          <span className="ml-3 font-mono text-xs text-muted-foreground">lesson_03.py</span>
        </div>
        <pre className="overflow-hidden p-5 font-mono text-[13px] leading-6 sm:text-sm">
          <code>
            <span className="text-[#a996ff]">def</span>{" "}
            <span className="text-accent">greet</span>(name):{"\n"}
            {"    "}<span className="text-[#a996ff]">return</span>{" "}
            <span className="text-[#34d399]">f&quot;Сәлем, {"{"}name{"}"}!&quot;</span>
            {"\n\n"}
            <span className="text-[#a996ff]">for</span> student{" "}
            <span className="text-[#a996ff]">in</span> [<span className="text-[#34d399]">&quot;Айбек&quot;</span>,{" "}
            <span className="text-[#34d399]">&quot;Аружан&quot;</span>]:{"\n"}
            {"    "}<span className="text-accent">print</span>(greet(student)){"\n\n"}
            <span className="text-muted-foreground"># ▶ Сәлем, Айбек!</span>{"\n"}
            <span className="text-muted-foreground"># ▶ Сәлем, Аружан!</span>
          </code>
        </pre>
      </div>
      <div className="absolute -left-4 top-1/3 hidden items-center gap-2 rounded-xl border border-border bg-card px-3 py-2 text-xs font-semibold shadow-xl sm:flex lg:hidden xl:flex">
        <CheckCircle2 className="size-4 text-success" /> Quiz · 10/10
      </div>
      <div className="absolute -right-3 -top-4 flex items-center gap-2 rounded-xl border border-border bg-card px-3 py-2 text-xs font-semibold shadow-xl">
        <Sparkles className="size-4 text-accent" /> STUD AI
      </div>
      <div className="absolute -bottom-5 right-8 flex items-center gap-2 rounded-xl border border-border bg-card px-3 py-2 text-xs font-semibold shadow-xl">
        <Trophy className="size-4 text-warning" /> +50 XP
      </div>
    </div>
  );
}
