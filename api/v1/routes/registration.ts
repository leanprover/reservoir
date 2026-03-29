import { z } from "zod"
import { type H3Event, createRouter, readBody, getRouterParams, getHeader } from 'h3'
import { getStore } from "@netlify/blobs"
import { mkJsonResponse, NotFound, InsufficientStorage, validateMethod, defineEventErrorHandler, InternalServerError, Unauthorized } from '../utils/error'
import { randomUUID } from 'crypto'
import { GitHubFullName } from "../utils/zod"
import type { Source } from '../../../site/utils/manifest'

const GitHubRepoData = z.object({
  node_id: z.string(),
  default_branch: z.string(),
})

export function getRegistrationStore() {
  return getStore('package-registrations')
}

function checkToken(event: H3Event) {
  if (event.context.reservoir.local) return
  const authHeader = getHeader(event, 'authorization')
  if (authHeader?.startsWith('Bearer ') && authHeader.slice(7) === process.env.AUTH_TOKEN) {
    return
  }
  throw new Unauthorized("Operation not permitted")
}

export const registrationRouter = createRouter()

// body is a partial `Source` filed in with GitHub info
const PostRegistrationsBody = z.object({
  type: z.literal('git').optional(),
  host: z.literal('github'),
  fullName: GitHubFullName,
  //TODO: Make customizatiable (needs analysis support)
  //defaultBranch: z.string().optional(),
  //subDir: z.string().optional(),
}).strict()

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
      checkToken(event)
      const {blobs} = await registrations.list()
      if (blobs.length > parseInt(process.env.REGISTRATION_LIMIT!)) {
        console.error(`${blobs.length} registrations; limit reached`)
        throw new InsufficientStorage("Registration limit reached")
      }
      // repository name passes validation
      const {fullName} = PostRegistrationsBody.parse(await readBody(event))
      const url = `https://api.github.com/repos/${fullName}`
      console.log(`Fetch ${url}`)
      const res = await fetch(url, {
        headers: {
          "Accept":"application/vnd.github+json",
          "X-Github-Next-Global-ID": "1",
        }
      })
      if (res.status == 200) {
        let repo: typeof GitHubRepoData._type
        const ghBody = await res.text()
        try {
          repo = GitHubRepoData.parse(JSON.parse(ghBody))
        } catch (e) {
          const info = e instanceof Error ? e.stack : e
          console.error(`Unexpected GitHub response: ${info}\nRaw response: ${JSON.stringify(ghBody)}`)
          throw new InternalServerError("Failed to retrieve GitHub repository data")
        }
        const src: Source = {
          type: "git",
          host: "github",
          id: repo.node_id,
          fullName: fullName,
          repoUrl: `https://github.com/${fullName}`,
          gitUrl: `https://github.com/${fullName}`,
          defaultBranch: repo.default_branch
        }
        const uuid = randomUUID()
        await registrations.set(uuid, JSON.stringify(src))
        return mkJsonResponse(uuid)
      } else if (res.status == 404) {
        console.log("GitHub repository not found")
        throw new NotFound("GitHub repository not found")
      } else {
        console.error(`Fetch failed (${res.status}): ${await res.text()}`)
        throw new InternalServerError("Failed to retrieve GitHub repository data")
      }
    }
    case "DELETE": {
      checkToken(event)
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
      checkToken(event)
      await registrations.delete(key)
      return mkJsonResponse(true)
    }
  }
}))
