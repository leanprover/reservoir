import { z } from 'zod'
import { getRouterParams, getQuery } from "h3"
import { validateMethod, defineEventErrorHandler } from '../utils/error'

export async function getArtifact(scope: string, hash: string, dev: boolean) {
  const key = `${dev ? 'a0' : 'a1'}/${scope}/${hash}.art`
  const url = `${process.env.S3_CDN_ENDPOINT}/${key}`
  return new Response(null, {status: 303, headers: {"Location": url}})
}

export function parseArtifact(file: string, ctx: z.RefinementCtx) {
  const dotIdx = file.indexOf('.')
  if (dotIdx < 0) return file
  const ext = file.slice(dotIdx+1)
  if (ext != 'art') {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: `Expected file extension to be 'art', got '${ext}'`,
      fatal: true,
    });
    return z.NEVER
  }
  const hash = file.slice(0, dotIdx)
  if (hash.length != 16) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: `Expected name with exactly 16 hexits`,
      fatal: true,
    });
    return z.NEVER
  }
  return hash
}

const GetArtifactParams = z.object({
  owner: z.string().min(1),
  repo: z.string().min(1),
  artifact: z.string().transform(parseArtifact),
})

export const artifactHandler = defineEventErrorHandler(event => {
  validateMethod(event.method, ["GET"])
  const {owner, repo, artifact} = GetArtifactParams.parse(getRouterParams(event, {decode: true}))
  return getArtifact(`${owner}/${repo}`, artifact, getQuery(event).dev != undefined)
})
