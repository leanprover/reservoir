import { mkError } from '../utils/error'
import { type Context as NetlifyContext } from "@netlify/functions"

export async function packageHandler(req: Request, context: NetlifyContext) {
  const {owner, name} = context.params
  const lakeVer = req.headers.get("X-Lake-Registry-Api-Version")
  const reservoirVer = req.headers.get("X-Reservoir-Api-Version")
  console.log(`${req.method} ${owner ?? ""}/${name ?? ""} Reservoir:${reservoirVer ?? "-"} Lake:${lakeVer ?? "-"}`)
  if (req.method !== "GET") {
    if (req.method === "HEAD") { // body not allowed
      return new Response(null, {status: 405, headers: {'Allow': 'GET'}})
    } else {
      return mkError(405, `${req.method} not allowed; can only GET packages`, {'Allow': 'GET'})
    }
  }
  if (!name) {
    return mkError(400, "Ill-formed package name")
  }
  if (!owner) {
    return mkError(400, "Ill-formed package owner")
  }
  const origin = new URL(req.url).origin
  const path = `${encodeURIComponent(owner.toLowerCase())}/${encodeURIComponent(name.toLowerCase())}`
  const fileUrl = `${origin}/index/${path}/metadata.json`
  console.log(`Fetch ${fileUrl}`)
  const res = await fetch(fileUrl)
  if (res.status == 200) {
    return new Response(res.body, {
      headers: {"Content-Type": "application/json; charset=utf-8"}
    })
  } else if (res.status == 404) {
    return mkError(404, `Package '${owner}/${name}' not found in index`)
  } else {
    console.error(`Fetch failed with status ${res.status}`)
    return mkError(500, "Failed to retrieve package data from index")
  }
};
