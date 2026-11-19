/** Privacy-enhanced YouTube embed (no tracking cookies until the user plays). */
export function YouTubePlayer({ videoId, title }: { videoId: string; title: string }) {
  // The id is validated by the backend (11 chars of [A-Za-z0-9_-]); re-check defensively.
  if (!/^[A-Za-z0-9_-]{11}$/.test(videoId)) return null;
  return (
    <div className="relative aspect-video w-full overflow-hidden rounded-2xl border border-border bg-black shadow-2xl shadow-black/40">
      <iframe
        src={`https://www.youtube-nocookie.com/embed/${videoId}?rel=0&hl=ru`}
        title={title}
        className="absolute inset-0 size-full"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        referrerPolicy="strict-origin-when-cross-origin"
        allowFullScreen
        loading="lazy"
      />
    </div>
  );
}
