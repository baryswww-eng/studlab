/**
 * Same-origin API proxy: the browser calls /api/v1/* on the site's own domain and
 * this handler forwards to the FastAPI backend (API_INTERNAL_URL). Benefits:
 * session cookies are first-party, no CORS in production, and the backend URL
 * can change without rebuilding the frontend. Streaming (SSE) responses pass through.
 */
import type { NextRequest } from "next/server";

export const dynamic = "force-dynamic";

const BACKEND = (process.env.API_INTERNAL_URL ?? "http://localhost:8000").replace(/\/$/, "");

// Request headers worth forwarding; everything else (host, connection, …) is dropped.
const FORWARD_REQUEST = ["accept", "content-type", "cookie", "user-agent", "accept-language"];
// Response headers that must not be copied (the body is already decoded/re-chunked).
const DROP_RESPONSE = new Set(["content-encoding", "content-length", "transfer-encoding", "connection"]);

async function proxy(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  const target = `${BACKEND}/api/v1/${path.map(encodeURIComponent).join("/")}${request.nextUrl.search}`;

  const headers = new Headers();
  for (const name of FORWARD_REQUEST) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }
  // Real client IP for backend rate limits.
  const clientIp =
    request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ?? request.headers.get("x-real-ip");
  if (clientIp) headers.set("x-forwarded-for", clientIp);

  const hasBody = !["GET", "HEAD"].includes(request.method);
  let upstream: Response;
  try {
    upstream = await fetch(target, {
      method: request.method,
      headers,
      body: hasBody ? await request.arrayBuffer() : undefined,
      redirect: "manual",
      cache: "no-store",
    });
  } catch {
    return Response.json(
      { error: { code: "backend_unreachable", message: "Backend is unreachable" } },
      { status: 502 },
    );
  }

  const responseHeaders = new Headers();
  upstream.headers.forEach((value, name) => {
    if (!DROP_RESPONSE.has(name) && name !== "set-cookie") responseHeaders.set(name, value);
  });
  for (const cookie of upstream.headers.getSetCookie()) responseHeaders.append("set-cookie", cookie);

  return new Response(upstream.body, { status: upstream.status, headers: responseHeaders });
}

export { proxy as DELETE, proxy as GET, proxy as PATCH, proxy as POST, proxy as PUT };
