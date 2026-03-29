import { type H3Event, getQuery } from "h3"

export interface ReservoirContext {
  apiVersion: string | null
  lakeApiVersion: string | null
  indexUrl: string
  local: boolean
  dev: boolean
}

declare module 'h3' {
  interface H3EventContext {
    reservoir: ReservoirContext
  }
}

export function isDev(event: H3Event, devParam?: boolean) {
  return event.context.reservoir.dev || (devParam ?? getQuery(event).dev != undefined)
}

export function initReservoirContext(event: H3Event) {
  const lakeVer = event.headers.get("X-Lake-Registry-Api-Version")
  const reservoirVer = event.headers.get("X-Reservoir-Api-Version")
  const local = event.context.netlify.deploy.context == "dev"
  console.log(`${event.method} Reservoir:${reservoirVer ?? "-"} Lake:${lakeVer ?? "-"} ${event.path} `)
  event.context.reservoir = {
    apiVersion: reservoirVer,
    lakeApiVersion: lakeVer,
    indexUrl: local
      ? "https://reservoir.lean-lang.org/index"
      : `${event.web!.url!.origin}/index`,
    dev: false,
    local
  }
}
