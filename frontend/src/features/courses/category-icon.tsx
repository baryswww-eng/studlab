import {
  Braces,
  BrainCircuit,
  Code2,
  Cpu,
  Database,
  FileCode2,
  Globe,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/lib/utils";

const ICONS: Record<string, LucideIcon> = {
  python: FileCode2,
  globe: Globe,
  braces: Braces,
  database: Database,
  brain: BrainCircuit,
  cpu: Cpu,
};

// Each direction has its own gradient so covers are recognizable without images.
const GRADIENTS: Record<string, string> = {
  python: "from-[#7856FF] to-[#38BDF8]",
  globe: "from-[#38BDF8] to-[#22D3EE]",
  braces: "from-[#8B5CF6] to-[#EC4899]",
  database: "from-[#0EA5E9] to-[#6366F1]",
  brain: "from-[#A855F7] to-[#38BDF8]",
  cpu: "from-[#14B8A6] to-[#7856FF]",
};

export function CategoryIcon({ icon, className }: { icon: string; className?: string }) {
  const Icon = ICONS[icon] ?? Code2;
  return <Icon className={className} aria-hidden="true" />;
}

export function categoryGradient(icon: string | undefined) {
  return GRADIENTS[icon ?? ""] ?? "from-[#7856FF] to-[#38BDF8]";
}

/** Branded cover used when a course has no uploaded cover image. */
export function CourseCover({
  icon,
  title,
  coverUrl,
  className,
}: {
  icon?: string;
  title: string;
  coverUrl: string | null;
  className?: string;
}) {
  if (coverUrl) {
    return (
      // eslint-disable-next-line @next/next/no-img-element -- covers come from S3 later; domains not fixed yet
      <img src={coverUrl} alt="" className={cn("aspect-[16/9] w-full object-cover", className)} />
    );
  }
  return (
    <div
      aria-hidden="true"
      className={cn(
        "relative flex aspect-[16/9] w-full items-center justify-center overflow-hidden bg-gradient-to-br",
        categoryGradient(icon),
        className,
      )}
    >
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_20%,rgba(255,255,255,0.25),transparent_45%)]" />
      <div className="absolute -bottom-6 -right-6 size-32 rounded-full border-[14px] border-white/10" />
      <CategoryIcon icon={icon ?? ""} className="relative size-14 text-white drop-shadow-lg" />
      <span className="sr-only">{title}</span>
    </div>
  );
}
