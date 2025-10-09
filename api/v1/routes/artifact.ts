import { z } from 'zod'
import { getRouterParams, getQuery } from "h3"
import { validateMethod, defineEventErrorHandler } from '../utils/error'
import { GitHubOwner, GitHubRepo, trimExt, validatePlatform, validateToolchain, toolchainToDir } from '../utils/zod'

/**
 * Redirect to the location of an artifact in cloud storage.
 *
 * `repo` and `hash` should be URL encoded.
 */
export async function getArtifact(repo: string, hash: string, dev: boolean) {
  const key = `${dev ? 'a0' : 'a1'}/${repo}/${hash}.art`
  const url = `${process.env.S3_CDN_ENDPOINT}/${key}`
  return new Response(null, {status: 303, headers: {"Location": url}})
}

/** Zod schema for extracting an artifact hash from a `<hash>.art` artifact file name. */
export const ArtifactFromFile = z.string()
  .transform((art, ctx) => trimExt('art', art, ctx))
  .refine(art => art.length == 16, "Expected name of exactly 16 hexits")

const GetArtifactParams = z.object({
  owner: GitHubOwner,
  repo: GitHubRepo,
  artifact: ArtifactFromFile,
})

export const artifactHandler = defineEventErrorHandler(event => {
  validateMethod(event.method, ["GET"])
  const {owner, repo, artifact} = GetArtifactParams.parse(getRouterParams(event, {decode: true}))
  const dev = event.context.reservoir.dev || getQuery(event).dev != undefined
  return getArtifact(`${owner}/${repo}`, artifact, dev)
})

/**
 * Redirect to the location of a build output file in cloud storage.
 *
 * `repo` and `rev` should be URL encoded.
 * `platform` and `toolchain` should have passed validation.
 */
export async function getRevisionOutputs(repo: string, rev: string, platform?: string, toolchain?: string, dev?: boolean) {
  let key = `${dev ? 'r0' : 'r1'}/${repo}`
  if (platform) {
    // platform is URI-safe, see `validatePlatform`
    key = `${key}/pt/${platform}`
  }
  if (toolchain) {
    // toolchain is URI-safe after `toolchainToDir`, see `validateToolchain`
    key = `${key}/tc/${toolchainToDir(toolchain)}`
  }
  key = `${key}/${rev}.jsonl`
  const url = `${process.env.S3_CDN_ENDPOINT}/${key}`
  return new Response(null, {status: 303, headers: {"Location": url}})
}

const BuildOutputsParams = z.object({
  owner: GitHubOwner,
  repo: GitHubRepo,
})

export const BuildOutputsQuery = z.object({
  rev: z.string().refine(rev => rev.length == 40, "Expected revision of exactly 40 hexits"),
  platform: z.string().transform(validatePlatform).optional(),
  toolchain: z.string().transform(validateToolchain).optional(),
  dev: z.any().optional().transform(dev => dev != undefined),
})

export const outputsHandler = defineEventErrorHandler(event => {
  validateMethod(event.method, ["GET"])
  const {owner, repo} = BuildOutputsParams.parse(getRouterParams(event))
  const {rev, platform, toolchain, dev} = BuildOutputsQuery.parse(getQuery(event))
  return getRevisionOutputs(`${owner}/${repo}`, rev, platform, toolchain, event.context.reservoir.dev || dev)
})
