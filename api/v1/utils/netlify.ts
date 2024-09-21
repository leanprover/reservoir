import { type Context as NetlifyContext } from "@netlify/functions"
import { defineEventHandler, toWebHandler, toWebRequest, type EventHandlerResponse, type App } from "h3";

declare module 'h3' {
  interface H3EventContext {
    netlify: NetlifyContext
  }
}

export type NetlifyHandler<T extends EventHandlerResponse<Response>> = (req: Request, context: NetlifyContext) => T

export function toNetlifyHandler(app: App): NetlifyHandler<Promise<Response>> {
  return (req: Request, context: NetlifyContext) => {
    return toWebHandler(app)(req, {netlify: context})
  }
}

export function fromNetlifyHandler<T extends EventHandlerResponse<Response>>(handler: NetlifyHandler<T>) {
  return defineEventHandler((event) => {
    const ctx = Object.assign(event.context.netlify, {params: event.context.params})
    return handler(toWebRequest(event), ctx)
  });
}
