"use client";

import { RefreshCw } from "lucide-react";
import { useRouter } from "next/navigation";
import { useTransition } from "react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

/** Re-runs the server-side health checks without a full page reload. */
export function RefreshButton({ label }: { label: string }) {
  const router = useRouter();
  const [isPending, startTransition] = useTransition();
  return (
    <Button
      variant="secondary"
      size="sm"
      disabled={isPending}
      aria-busy={isPending}
      onClick={() => startTransition(() => router.refresh())}
    >
      <RefreshCw className={cn(isPending && "animate-spin")} aria-hidden="true" />
      {label}
    </Button>
  );
}
