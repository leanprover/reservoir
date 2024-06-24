import { type Config, type Context } from "@netlify/functions"

function error(status: number, message: string, headers: HeadersInit = {}): Response {
  return new Response(JSON.stringify({"error": {status, message}}), {
    status, headers: {"Content-Type": "application/json; charset=utf-8", ...headers}
  })
}

export default async (req: Request, context: Context) => {
  const {owner, name} = context.params
  const lakeVer = req.headers.get("X-Lake-Registry-Api-Version")
  const reservoirVer = req.headers.get("X-Reservoir-Api-Version")
  console.log(`${req.method} ${owner ?? ""}/${name ?? ""} Reservoir:${reservoirVer ?? "-"} Lake:${lakeVer ?? "-"}`)
  if (req.method !== "GET") {
    if (req.method === "HEAD") { // body not allowed
      return new Response(null, {status: 405, headers: {'Allow': 'GET'}})
    } else {
      return error(405, `${req.method} not allowed; can only GET packages`, {'Allow': 'GET'})
    }
  }
  if (!name) {
    return error(400, "Ill-formed package name")
  }
  if (!owner) {
    return error(400, "Ill-formed package owner")
  }
  const path = `${encodeURIComponent(owner.toLowerCase())}/${encodeURIComponent(name.toLowerCase())}`
  const fileUrl = `${new URL(req.url).origin}/index/${path}/metadata.json`
  console.log(`Fetch ${fileUrl}`)
  const res = await fetch(fileUrl)
  if (res.status == 200) {
    return new Response(res.body, {
      headers: {"Content-Type": "application/json; charset=utf-8"}
    })
  } else if (res.status == 404) {
    return error(404, `Package  '${owner}/${name}' not found in index`)
  } else {
    console.error(`Fetch failed with status ${res.status}`)
    return error(500, "Failed to retrieve package data from index")
  }
};

export const config: Config = {
  path: [
    "/api/packages/:owner/:name",
    "/api/v1/packages/:owner/:name",
    "/api/v0/packages/:owner/:name",
  ]
}
