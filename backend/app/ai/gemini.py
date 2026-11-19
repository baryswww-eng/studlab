"""Minimal Google Gemini REST client (generateContent) with model fallback.

Uses the public REST API directly via httpx — no extra SDK dependency. The API
key is sent in the `x-goog-api-key` header (never in the URL, so it does not end
up in access logs).
"""

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Literal

import httpx

logger = logging.getLogger("app.ai")

API_BASE = "https://generativelanguage.googleapis.com/v1beta"

Role = Literal["user", "model"]


@dataclass(frozen=True)
class ChatTurn:
    role: Role
    text: str


@dataclass(frozen=True)
class GeminiReply:
    text: str
    model: str
    prompt_tokens: int
    output_tokens: int


@dataclass(frozen=True)
class StreamChunk:
    text: str
    model: str
    done: bool = False
    prompt_tokens: int = 0
    output_tokens: int = 0


class GeminiError(Exception):
    """Base error. `retryable` → another model may succeed (quota, overload)."""

    def __init__(
        self,
        message: str,
        *,
        retryable: bool = False,
        blocked: bool = False,
        transient: bool = False,
    ):
        super().__init__(message)
        self.retryable = retryable or transient
        self.blocked = blocked
        # Temporary overload (500/503/504): the same model may answer after a short pause.
        self.transient = transient


class GeminiClient:
    # Seconds of silence after which the next model is raced in parallel.
    HEDGE_DELAY = 6.0

    def __init__(
        self, api_key: str, timeout: float = 60, transport: httpx.AsyncBaseTransport | None = None
    ):
        self._api_key = api_key
        self._timeout = timeout
        self._transport = transport

    async def _generate(
        self,
        model: str,
        system: str,
        turns: list[ChatTurn],
        max_tokens: int,
        json_mode: bool = False,
    ) -> GeminiReply:
        payload = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": t.role, "parts": [{"text": t.text}]} for t in turns],
            "generationConfig": {"temperature": 0.6, "maxOutputTokens": max_tokens},
        }
        if json_mode:
            payload["generationConfig"]["responseMimeType"] = "application/json"  # type: ignore[index]
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout, transport=self._transport
            ) as client:
                response = await client.post(
                    f"{API_BASE}/models/{model}:generateContent",
                    json=payload,
                    headers={"x-goog-api-key": self._api_key},
                )
        except httpx.HTTPError as exc:
            raise GeminiError(f"network error: {type(exc).__name__}", retryable=True) from exc

        if response.status_code in (500, 503, 504):
            raise GeminiError(f"{model}: HTTP {response.status_code}", transient=True)
        if response.status_code in (404, 429):
            # 429 quota exhausted, 404 model not available for this key → next model.
            raise GeminiError(f"{model}: HTTP {response.status_code}", retryable=True)
        if response.status_code >= 400:
            raise GeminiError(f"{model}: HTTP {response.status_code}")

        data = response.json()
        if (data.get("promptFeedback") or {}).get("blockReason"):
            raise GeminiError("prompt blocked by safety filters", blocked=True)
        candidates = data.get("candidates") or []
        parts = ((candidates[0].get("content") or {}).get("parts") or []) if candidates else []
        text = "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
        if not text:
            reason = candidates[0].get("finishReason") if candidates else "NO_CANDIDATES"
            raise GeminiError(f"empty answer ({reason})", blocked=reason == "SAFETY")
        usage = data.get("usageMetadata") or {}
        return GeminiReply(
            text=text,
            model=model,
            prompt_tokens=int(usage.get("promptTokenCount", 0)),
            output_tokens=int(usage.get("candidatesTokenCount", 0)),
        )

    async def generate(
        self,
        models: list[str],
        system: str,
        turns: list[ChatTurn],
        max_tokens: int = 4096,
        json_mode: bool = False,
    ) -> GeminiReply:
        """Hedged request: start the next model if the current one is silent for
        HEDGE_DELAY seconds (or fails), return the first successful answer."""
        queue = list(models)
        running: dict[asyncio.Task[GeminiReply], str] = {}
        last: GeminiError | None = None

        def start_next() -> None:
            model = queue.pop(0)
            task = asyncio.create_task(self._generate(model, system, turns, max_tokens, json_mode))
            running[task] = model

        try:
            if queue:
                start_next()
            while running:
                done, _ = await asyncio.wait(
                    running,
                    timeout=self.HEDGE_DELAY if queue else None,
                    return_when=asyncio.FIRST_COMPLETED,
                )
                if not done:  # current model(s) are slow: race the next one
                    start_next()
                    continue
                for task in done:
                    running.pop(task)
                    exc = task.exception()
                    if exc is None:
                        return task.result()
                    if not isinstance(exc, GeminiError):
                        raise exc
                    logger.warning("Gemini call failed: %s", exc)
                    last = exc
                    if not exc.retryable:
                        raise exc
                if not running and queue:
                    start_next()
        finally:
            for task in running:
                task.cancel()
        raise last or GeminiError("no models configured")

    async def _stream(
        self, model: str, system: str, turns: list[ChatTurn], max_tokens: int
    ) -> AsyncIterator[StreamChunk]:
        payload = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": t.role, "parts": [{"text": t.text}]} for t in turns],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": max_tokens},
        }
        prompt_tokens = output_tokens = 0
        got_text = False
        try:
            async with (
                httpx.AsyncClient(timeout=self._timeout, transport=self._transport) as client,
                client.stream(
                    "POST",
                    f"{API_BASE}/models/{model}:streamGenerateContent",
                    params={"alt": "sse"},
                    json=payload,
                    headers={"x-goog-api-key": self._api_key},
                ) as response,
            ):
                if response.status_code in (500, 503, 504):
                    raise GeminiError(f"{model}: HTTP {response.status_code}", transient=True)
                if response.status_code in (404, 429):
                    raise GeminiError(f"{model}: HTTP {response.status_code}", retryable=True)
                if response.status_code >= 400:
                    raise GeminiError(f"{model}: HTTP {response.status_code}")
                async for line in response.aiter_lines():
                    if not line.startswith("data:"):
                        continue
                    try:
                        data = json.loads(line[5:].strip())
                    except json.JSONDecodeError:
                        continue
                    if (data.get("promptFeedback") or {}).get("blockReason"):
                        raise GeminiError("prompt blocked by safety filters", blocked=True)
                    for cand in data.get("candidates") or []:
                        for part in (cand.get("content") or {}).get("parts") or []:
                            text = part.get("text", "")
                            if text and not part.get("thought"):
                                got_text = True
                                yield StreamChunk(text=text, model=model)
                    usage = data.get("usageMetadata") or {}
                    prompt_tokens = int(usage.get("promptTokenCount", prompt_tokens))
                    output_tokens = int(usage.get("candidatesTokenCount", output_tokens))
        except httpx.HTTPError as exc:
            raise GeminiError(
                f"network error: {type(exc).__name__}", retryable=not got_text
            ) from exc
        if not got_text:
            raise GeminiError(f"{model}: empty answer", retryable=True)
        yield StreamChunk(
            text="",
            model=model,
            done=True,
            prompt_tokens=prompt_tokens,
            output_tokens=output_tokens,
        )

    async def stream(
        self, models: list[str], system: str, turns: list[ChatTurn], max_tokens: int = 8192
    ) -> AsyncIterator[StreamChunk]:
        """Hedged streaming: if no text arrives within HEDGE_DELAY seconds, the next
        model is started in parallel; the first model to produce text wins and the
        others are cancelled. After text has started there is no fallback."""
        queue = list(models)
        racers: dict[str, tuple[asyncio.Task[None], asyncio.Queue[object]]] = {}
        last: GeminiError | None = None
        end = object()

        async def pump(model: str, out: asyncio.Queue[object]) -> None:
            try:
                async for chunk in self._stream(model, system, turns, max_tokens):
                    await out.put(chunk)
                await out.put(end)
            except GeminiError as exc:
                await out.put(exc)

        def start_next() -> None:
            model = queue.pop(0)
            out: asyncio.Queue[object] = asyncio.Queue()
            racers[model] = (asyncio.create_task(pump(model, out)), out)

        winner: asyncio.Queue[object] | None = None
        try:
            if queue:
                start_next()
            while winner is None:
                if not racers:
                    if not queue:
                        raise last or GeminiError("no models configured")
                    start_next()
                getters = {
                    asyncio.create_task(out.get()): model for model, (_, out) in racers.items()
                }
                done, pending = await asyncio.wait(
                    getters,
                    timeout=self.HEDGE_DELAY if queue else None,
                    return_when=asyncio.FIRST_COMPLETED,
                )
                for g in pending:
                    g.cancel()
                if not done:
                    start_next()
                    continue
                for g in done:
                    model = getters[g]
                    item = g.result()
                    if isinstance(item, StreamChunk) and winner is None:
                        winner = racers[model][1]
                        for other, (task, _) in list(racers.items()):
                            if other != model:
                                task.cancel()
                                racers.pop(other)
                        yield item
                    elif isinstance(item, GeminiError):
                        logger.warning("Gemini stream failed: %s", item)
                        last = item
                        racers.pop(model, None)
                        if not item.retryable:
                            raise item
                    elif item is end:
                        racers.pop(model, None)
            while True:  # forward the winner's remaining chunks
                item = await winner.get()
                if item is end:
                    return
                if isinstance(item, GeminiError):
                    raise item
                assert isinstance(item, StreamChunk)
                yield item
        finally:
            for task, _ in racers.values():
                task.cancel()
