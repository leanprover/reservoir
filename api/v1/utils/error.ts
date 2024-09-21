export function mkError(status: number, message: string, headers: HeadersInit = {}): Response {
  return new Response(JSON.stringify({"error": {status, message}}), {
    status, headers: {"Content-Type": "application/json; charset=utf-8", ...headers}
  })
}
