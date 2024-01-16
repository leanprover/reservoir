import { type Config, type Context } from "@netlify/functions"

export default async (_req: Request, context: Context) => {
  const {owner, name} = context.params
  if (!owner || !name) {
    return new Response(null, {status: 404})
  }
  const path = `${encodeURIComponent(owner)}/${encodeURIComponent(name)}`
  const fileUrl = `${context.site.url}/index/${path}/metadata.json`
  console.log(`fetch ${fileUrl}`)
  const res = await fetch(fileUrl)
  return new Response(res.body, {
    headers: {"content-type": "text/event-stream"}
  })
};

export const config: Config = {
  path: "/api/v0/packages/:owner/:name"
}
