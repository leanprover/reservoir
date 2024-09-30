import { type Context } from "@netlify/functions"
import { defineEventHandler, toWebHandler, toWebRequest, getRouterParams } from "h3"
import type { EventHandlerResponse, App } from "h3"

/**
 * The publicly documented fields of Netlify's context object.
 * @see https://docs.netlify.com/functions/api/#netlify-specific-context-object
 */
type NetlifyContext = Pick<Context,
  'account' | 'cookies' | 'deploy' | 'flags' | 'geo' |
  'ip' | 'params'| 'requestId' | 'server' | 'site'>

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
    const params = getRouterParams(event)
    const ctx = Object.assign(event.context.netlify, {params})
    return handler(toWebRequest(event), ctx)
  });
}
