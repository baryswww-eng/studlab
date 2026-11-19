"use client";

import { AlertTriangle, Bot, Loader2, RotateCcw, Send, Square, UserRound } from "lucide-react";
import { useTranslations } from "next-intl";
import { type FormEvent, type KeyboardEvent, useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/features/auth/auth-provider";
import { cn } from "@/lib/utils";
import { AI_MODES, type AIMode, type ChatMessage, getAIStatus, streamChat } from "@/services/ai";
import { Markdown } from "./markdown";

type Status = "loading" | "enabled" | "disabled";

export function AIChat({ lessonId, compact = false }: { lessonId?: number; compact?: boolean }) {
  const t = useTranslations("ai");
  const { user } = useAuth();
  const [status, setStatus] = useState<Status>("loading");
  const [mode, setMode] = useState<AIMode>(lessonId ? "tutor" : "chat");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streaming, setStreaming] = useState<string | null>(null); // answer being typed
  const [input, setInput] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [remaining, setRemaining] = useState<number | null>(null);
  const listRef = useRef<HTMLDivElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    let cancelled = false;
    getAIStatus()
      .then((s) => !cancelled && setStatus(s.enabled ? "enabled" : "disabled"))
      .catch(() => !cancelled && setStatus("disabled"));
    return () => {
      cancelled = true;
      abortRef.current?.abort();
    };
  }, []);

  // Keep the newest text in view while the answer streams in.
  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight });
  }, [messages, streaming, pending]);

  async function ask(text: string) {
    const message = text.trim();
    if (!message || pending || status !== "enabled") return;
    setError(null);
    setInput("");
    const history = messages;
    setMessages([...history, { role: "user", content: message }]);
    setPending(true);
    setStreaming("");

    const controller = new AbortController();
    abortRef.current = controller;
    let answer = "";
    let failed = false;

    await streamChat(
      { message, mode, lessonId, conversationId, history },
      {
        onDelta: (chunk) => {
          answer += chunk;
          setStreaming(answer);
        },
        onDone: (info) => {
          setConversationId(info.conversation_id);
          setRemaining(info.remaining_today);
        },
        onError: (msg) => {
          failed = true;
          setError(msg ?? t("error"));
        },
      },
      controller.signal,
    );

    abortRef.current = null;
    setPending(false);
    setStreaming(null);
    if (answer) {
      // Keep what was generated (also after "Stop" or a mid-answer error).
      setMessages((m) => [...m, { role: "model", content: answer }]);
    } else if (failed || controller.signal.aborted) {
      setMessages(history); // nothing came back: roll back the question…
      setInput(message); // …and give it back to edit/retry
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    void ask(input);
  }

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault();
      void ask(input);
    }
  }

  function reset() {
    abortRef.current?.abort();
    setMessages([]);
    setConversationId(null);
    setError(null);
  }

  const disabled = status !== "enabled";
  const suggestions = t.raw(`suggestions.${mode}`) as string[];
  const modes = lessonId ? AI_MODES.filter((m) => m !== "chat") : AI_MODES;

  return (
    <div className="flex flex-col overflow-hidden rounded-2xl border border-border bg-card">
      {/* Mode switcher */}
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-border p-3">
        <div role="radiogroup" aria-label={t("modeLabel")} className="flex flex-wrap gap-1">
          {modes.map((m) => (
            <button
              key={m}
              type="button"
              role="radio"
              aria-checked={mode === m}
              onClick={() => setMode(m)}
              className={cn(
                "rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                mode === m
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground",
              )}
            >
              {t(`modes.${m}`)}
            </button>
          ))}
        </div>
        {messages.length > 0 && (
          <Button variant="ghost" size="sm" onClick={reset}>
            <RotateCcw aria-hidden="true" />
            {t("clear")}
          </Button>
        )}
      </div>

      {/* Messages */}
      <div
        ref={listRef}
        aria-live="polite"
        aria-busy={pending}
        className={cn(
          "flex flex-col gap-4 overflow-y-auto p-4",
          compact ? "max-h-[30rem] min-h-40" : "h-[min(65vh,42rem)]",
        )}
      >
        {status === "disabled" && (
          <p
            role="alert"
            className="flex items-start gap-2 rounded-xl border border-warning/40 bg-warning/10 p-3 text-sm text-warning"
          >
            <AlertTriangle className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
            {t("notConfigured")}
          </p>
        )}

        {messages.length === 0 && status === "enabled" && (
          <div className="flex flex-col gap-2">
            {suggestions.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => void ask(s)}
                className="w-fit rounded-xl border border-border bg-background/40 px-3 py-2 text-left text-sm text-muted-foreground transition-colors hover:border-primary/50 hover:text-foreground"
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {messages.map((m, i) => (
          <MessageBubble key={i} role={m.role} youLabel={t("you")} botLabel={t("bot")}>
            {m.content}
          </MessageBubble>
        ))}

        {pending && (
          <MessageBubble role="model" youLabel={t("you")} botLabel={t("bot")}>
            {streaming ? (
              `${streaming}▍`
            ) : (
              <span className="flex items-center gap-2 py-1 text-sm text-muted-foreground">
                <Loader2 className="size-4 animate-spin" aria-hidden="true" />
                {t("thinking")}
              </span>
            )}
          </MessageBubble>
        )}
      </div>

      {/* Input */}
      <form onSubmit={onSubmit} className="flex flex-col gap-2 border-t border-border p-3">
        {error && (
          <p role="alert" className="flex items-start gap-2 text-sm text-warning">
            <AlertTriangle className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
            {error}
          </p>
        )}
        <div className="flex items-end gap-2">
          <label htmlFor={`ai-input-${lessonId ?? "main"}`} className="sr-only">
            {t("inputLabel")}
          </label>
          <textarea
            id={`ai-input-${lessonId ?? "main"}`}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
            maxLength={4000}
            rows={mode === "code" ? 5 : 2}
            disabled={disabled}
            placeholder={t(`placeholder.${mode}`)}
            className={cn(
              "min-h-11 w-full resize-y rounded-lg border border-input bg-background/60 px-3.5 py-2.5 text-sm text-foreground",
              "placeholder:text-muted-foreground/70 focus-visible:border-ring focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/30 disabled:opacity-50",
              mode === "code" && "font-mono",
            )}
          />
          {pending ? (
            <Button
              type="button"
              size="icon"
              variant="secondary"
              aria-label={t("stop")}
              title={t("stop")}
              onClick={() => abortRef.current?.abort()}
            >
              <Square className="fill-current" />
            </Button>
          ) : (
            <Button type="submit" size="icon" disabled={disabled || !input.trim()} aria-label={t("send")}>
              <Send />
            </Button>
          )}
        </div>
        <p className="flex flex-wrap justify-between gap-2 text-xs text-muted-foreground">
          <span>{t("hint")}</span>
          <span>
            {remaining !== null ? t("remaining", { count: remaining }) : !user ? t("anonNote") : null}
            {" · "}
            {t("disclaimer")}
          </span>
        </p>
      </form>
    </div>
  );
}

function MessageBubble({
  role,
  children,
  youLabel,
  botLabel,
}: {
  role: "user" | "model";
  children: React.ReactNode;
  youLabel: string;
  botLabel: string;
}) {
  const isUser = role === "user";
  return (
    <div className={cn("flex gap-3", isUser && "flex-row-reverse")}>
      <span
        aria-hidden="true"
        className={cn(
          "flex size-8 shrink-0 items-center justify-center rounded-full",
          isUser ? "bg-secondary" : "bg-gradient-to-br from-primary to-accent text-white",
        )}
      >
        {isUser ? <UserRound className="size-4" /> : <Bot className="size-4" />}
      </span>
      <div
        className={cn(
          "min-w-0 max-w-[85%] rounded-2xl px-4 py-2",
          isUser
            ? "whitespace-pre-wrap bg-primary/20 text-sm leading-6"
            : "border border-border bg-background/40",
        )}
      >
        <span className="sr-only">{isUser ? youLabel : botLabel}: </span>
        {isUser || typeof children !== "string" ? children : <Markdown>{children}</Markdown>}
      </div>
    </div>
  );
}
