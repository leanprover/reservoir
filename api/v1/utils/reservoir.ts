import type { H3Event } from "h3"

export interface ReservoirContext {
  apiVersion: string | null
  lakeApiVersion: string | null
  indexUrl: string
}

declare module 'h3' {
  interface H3EventContext {
    reservoir: ReservoirContext
  }
}

export function initReservoirContext(event: H3Event) {
  const lakeVer = event.headers.get("X-Lake-Registry-Api-Version")
  const reservoirVer = event.headers.get("X-Reservoir-Api-Version")
  console.log(`${event.method} Reservoir:${reservoirVer ?? "-"} Lake:${lakeVer ?? "-"} ${event.path} `)
  event.context.reservoir = {
    apiVersion: reservoirVer,
    lakeApiVersion: lakeVer,
    //indexUrl: `${event.web!.url!.origin}/index`,
    indexUrl: 'https://ju9jldr4lttgij4vxadp36u3zb8--reservoir-lean-lang.netlify.app/index',
  }
}
