import { type Config, type Context } from "@netlify/functions"

export default async (req: Request, context: Context) => {
  const {owner, name} = context.params
  if (!owner || !name) {
    return new Response(null, {status: 404})
  }
  const path = `${encodeURIComponent(owner.toLowerCase())}/${encodeURIComponent(name.toLowerCase())}`
  const fileUrl = `${new URL(req.url).origin}/index/${path}/metadata.json`
  console.log(`fetch ${fileUrl}`)
  const res = await fetch(fileUrl)
  if (res.status == 200) {
    return new Response(res.body, {
      headers: {"Content-Type": "text/event-stream"}
    })
  } else {
    return new Response(null, {status: res.status})
  }
};

export const config: Config = {
  path: "/api/v0/packages/:owner/:name"
}
