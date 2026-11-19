import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/**
 * Renders AI answers. react-markdown does not render raw HTML (no XSS from
 * model output); links open in a new tab without referrer/opener.
 */
export function Markdown({ children }: { children: string }) {
  return (
    <div className="ai-markdown text-sm leading-7">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          a: ({ href, children: c }) => (
            <a href={href} target="_blank" rel="noopener noreferrer nofollow" className="text-accent underline">
              {c}
            </a>
          ),
          pre: ({ children: c }) => (
            <pre className="my-3 overflow-x-auto rounded-xl border border-border bg-[#0b111e] p-4 font-mono text-[13px] leading-6">
              {c}
            </pre>
          ),
          code: ({ className, children: c }) =>
            className ? (
              <code className={className}>{c}</code>
            ) : (
              <code className="rounded bg-secondary px-1.5 py-0.5 font-mono text-[0.85em] text-[#c4b5fd]">{c}</code>
            ),
          h1: ({ children: c }) => <h3 className="mb-2 mt-4 text-lg font-bold">{c}</h3>,
          h2: ({ children: c }) => <h3 className="mb-2 mt-4 text-base font-bold">{c}</h3>,
          h3: ({ children: c }) => <h4 className="mb-1 mt-3 font-semibold">{c}</h4>,
          ul: ({ children: c }) => <ul className="my-2 list-disc space-y-1 pl-5">{c}</ul>,
          ol: ({ children: c }) => <ol className="my-2 list-decimal space-y-1 pl-5">{c}</ol>,
          p: ({ children: c }) => <p className="my-2">{c}</p>,
          table: ({ children: c }) => (
            <div className="my-3 overflow-x-auto">
              <table className="w-full border-collapse text-left text-sm [&_td]:border [&_td]:border-border [&_td]:px-3 [&_td]:py-1.5 [&_th]:border [&_th]:border-border [&_th]:bg-secondary [&_th]:px-3 [&_th]:py-1.5">
                {c}
              </table>
            </div>
          ),
          blockquote: ({ children: c }) => (
            <blockquote className="my-2 border-l-2 border-accent pl-3 text-muted-foreground">{c}</blockquote>
          ),
        }}
      >
        {children}
      </ReactMarkdown>
    </div>
  );
}
