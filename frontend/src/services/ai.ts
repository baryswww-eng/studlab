import { ApiError, apiBaseUrl, apiFetch } from "@/lib/api";

export type AIMode = "chat" | "tutor" | "code" | "quiz" | "practice";
export const AI_MODES: AIMode[] = ["chat", "tutor", "code", "quiz", "practice"];

export interface ChatMessage {
  role: "user" | "model";
  content: string;
}

export interface AIStatus {
  enabled: boolean;
  model: string | null;
  hourly_limit: number;
}

export function getAIStatus() {
  return apiFetch<AIStatus>("/ai/status", { cache: "no-store" });
}

export interface StreamDone {
  conversation_id: number | null;
  remaining_today: number | null;
  model: string;
}

export interface StreamHandlers {
  onDelta: (text: string) => void;
  onDone: (info: StreamDone) => void;
  onError: (message: string | null) => void;
}

type StreamEvent =
  | { type: "delta"; text: string }
  | ({ type: "done" } & StreamDone)
  | { type: "error"; message: string };

/**
 * Streams the answer from POST /ai/chat/stream (Server-Sent Events) so text
 * appears as it is generated, like in ChatGPT. Abort with the given signal.
 */
export async function streamChat(
  input: {
    message: string;
    mode: AIMode;
    lessonId?: number;
    conversationId: number | null;
    history: ChatMessage[];
  },
  handlers: StreamHandlers,
  signal: AbortSignal,
): Promise<void> {
  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl()}/api/v1/ai/chat/stream`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
      body: JSON.stringify({
        message: input.message,
        mode: input.mode,
        lesson_id: input.lessonId,
        conversation_id: input.conversationId ?? undefined,
        history: input.history.slice(-12),
      }),
      signal,
    });
  } catch (error) {
    if ((error as Error).name !== "AbortError") handlers.onError(null);
    return;
  }

  if (!response.ok || !response.body) {
    // Limits / config errors come back as normal JSON before the stream starts.
    const body = (await response.json().catch(() => null)) as { error?: { message?: string } } | null;
    handlers.onError(body?.error?.message ?? null);
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  try {
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      let sep: number;
      while ((sep = buffer.indexOf("\n\n")) !== -1) {
        const raw = buffer.slice(0, sep);
        buffer = buffer.slice(sep + 2);
        const line = raw.split("\n").find((l) => l.startsWith("data:"));
        if (!line) continue;
        const event = JSON.parse(line.slice(5).trim()) as StreamEvent;
        if (event.type === "delta") handlers.onDelta(event.text);
        else if (event.type === "done") handlers.onDone(event);
        else handlers.onError(event.message);
      }
    }
  } catch (error) {
    if ((error as Error).name !== "AbortError") handlers.onError(null);
  }
}

export { ApiError };
