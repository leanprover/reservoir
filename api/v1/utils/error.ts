import { ZodError } from 'zod'
import { defineEventHandler } from "h3"
import type { EventHandler, EventHandlerRequest, EventHandlerResponse, HTTPMethod } from "h3"

export interface ResponseErrorOptions extends ErrorOptions {
  headers?: HeadersInit
}

export class ResponseError extends Error {
  status: number
  headers: Headers

  constructor(status: number, message?: string, options?: ResponseErrorOptions) {
    super(message, options)
    this.status = status
    this.headers = new Headers(options?.headers)
  }
}

export class NotFound extends ResponseError {
  constructor(message?: string, options?: ResponseErrorOptions) {
    super(404, message, options)
  }
}

export class InternalServerError extends ResponseError {
  constructor(message?: string, options?: ResponseErrorOptions) {
    super(500, message, options)
  }
}


export class MethodNotAllowed extends ResponseError {
  method: string
  allow: HTTPMethod[]

  constructor(method: string, allow: HTTPMethod[], options?: ResponseErrorOptions) {
    const message = `${method} not allowed; supports: ${allow.join(', ')}`
    super(405, message, options);
    this.method = method
    this.allow = allow
    if (!this.headers.has('Allow')) {
      this.headers.append('Allow', allow.join(','))
    }
  }
}

export function validateMethod(method: string, allow: HTTPMethod[]) {
  if (!(allow as string[]).includes(method)) {
    throw new MethodNotAllowed(method, allow)
  }
}

export interface ReservoirError {
  status: number
  message: string
}

export interface ReservoirErrorBody {
  error: ReservoirError
}

export function mkError(status: number, message: string, headers: HeadersInit = {}): Response {
  const body: ReservoirErrorBody = {"error": {status, message}}
  return new Response(JSON.stringify(body), {
    status, headers: {"Content-Type": "application/json; charset=utf-8", ...headers}
  })
}

export function defineEventErrorHandler<
  Request extends EventHandlerRequest = EventHandlerRequest,
  Response extends EventHandlerResponse = EventHandlerResponse
  >(handler: EventHandler<Request, Response>)
{
  return defineEventHandler(async event => {
    try {
      return await handler(event)
    } catch (e) {
      // h3 handles removing the body on `HEAD` requests
      if (e instanceof ResponseError) {
        return mkError(e.status, e.message, e.headers)
      } else if (e instanceof ZodError) {
        const message = e.issues.map(issue => {
          const field = issue.path.reduce((str, elem) => {
            if (typeof elem == 'string') {
              return str + elem
            } else {
              return `${str}[${elem}]`
            }
          }, '')
          if (issue.message == 'Required') {
            return `Missing ${field}`
          } else {
            return `Invalid ${field}: ${issue.message}`
          }
        }).join('; ')
        return mkError(400, message)
      } else {
        const info = e instanceof Error ? e.stack : e
        console.error(`Unhandled server error: ${info}`)
        return mkError(500, 'Internal server error')
      }
    }
  })
}
