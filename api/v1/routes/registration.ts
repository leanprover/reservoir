import { z } from "zod"
import { createRouter, readBody } from 'h3'
import { getStore } from "@netlify/blobs"
import { mkJsonResponse, NotFound, validateMethod, defineEventErrorHandler } from '../utils/error'
import { randomUUID } from 'crypto'

export function getRegistrationStore() {
  return getStore('package-registrations')
}

export const registrationRouter = createRouter()

const DeleteRegistrationsBody = z.array(z.string()).optional()

registrationRouter.use('/registrations', defineEventErrorHandler(async event => {
  validateMethod(event.method, ["GET", "POST", "DELETE"])
  const registrations = getRegistrationStore()
  switch (event.method) {
    case "GET": {
      const {blobs} = await registrations.list()
      const pairs = await Promise.all(blobs.map(async ({key}) => {
        const registration = await registrations.get(key)
        return [key, JSON.parse(registration)]
      }))
      return mkJsonResponse({"data": Object.fromEntries(pairs)})
    }
    case "POST": {
      const uuid = randomUUID()
      await registrations.set(uuid, JSON.stringify(await readBody(event)))
      return mkJsonResponse(uuid)
    }
    case "DELETE": {
      const keys = DeleteRegistrationsBody.parse(await readBody(event))
      if (keys) {
        await Promise.all(keys.map(key => registrations.delete(key)))
        return mkJsonResponse(true)
      } else {
        const {blobs} = await registrations.list()
        await Promise.all(blobs.map(({key}) => registrations.delete(key)))
        return mkJsonResponse(blobs.map((({key}) => key)))
      }
    }
  }
}))

const RegistrationParams = z.object({key: z.string()})

registrationRouter.use('/registrations/:key', defineEventErrorHandler(async event => {
  validateMethod(event.method, ["GET", "DELETE"])
  const registrations = getRegistrationStore()
  const {key} = RegistrationParams.parse(getRouterParams(event))
  switch (event.method) {
    case "GET": {
      const data = await registrations.get(key)
      if (data == null) {
        throw new NotFound("Package registration not found")
      } else {
        return mkJsonResponse(data)
      }
    }
    case "DELETE": {
      await registrations.delete(key)
      return mkJsonResponse(true)
    }
  }
}))
