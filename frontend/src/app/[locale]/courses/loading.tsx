import { Skeleton } from "@/components/ui/states";

export default function Loading() {
  return (
    <div className="mx-auto w-full max-w-6xl px-4 py-12 sm:px-6" aria-busy="true">
      <Skeleton className="h-10 w-64" />
      <Skeleton className="mt-3 h-5 w-96 max-w-full" />
      <Skeleton className="mt-8 h-24 w-full rounded-2xl" />
      <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }, (_, i) => (
          <Skeleton key={i} className="h-96 rounded-2xl" />
        ))}
      </div>
    </div>
  );
}
