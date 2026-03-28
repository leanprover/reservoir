import { z } from 'zod'
import { getRouterParams, getQuery, readBody } from "h3"
import { validateMethod, defineEventErrorHandler, mkJsonReponse } from '../utils/error'
import { GitRev, GitHubOwner, GitHubRepo, trimExt, validatePlatform, validateToolchain, toolchainToDir, isFixedHex, Dev } from '../utils/zod'
import { isDev } from '../utils/reservoir'

/** Zod schema for the URL params of a repository endpoint. */
const RepoParams = z.object({
  owner: GitHubOwner,
  repo: GitHubRepo,
})

/**
 * Redirect to the location of an artifact in cloud storage.
 *
 * `repo` and `hash` should have passed validation.
 */
export async function getArtifact(repo: string, hash: string, dev: boolean) {
  const key = `${dev ? 'a0' : 'a1'}/${repo}/${hash}.art`
  const url = `${process.env.S3_CDN_ENDPOINT}/${key}`
  return new Response(null, {status: 303, headers: {"Location": url}})
}

/**
 * Returns a list of artifact urls in the cloud storage.
 *
 * `repo` and `hash` should have passed validation.
 */
export async function getArtifactUrls(repo: string, hashes: string[], dev: boolean) {
  const baseUrl = `${process.env.S3_CDN_ENDPOINT}/${dev ? 'a0' : 'a1'}/${repo}`
  const urls = hashes.map(hash => `${baseUrl}/${hash}.art`)
  return mkJsonReponse(urls)
}

/** Zod schema for an artifact hash. */
export const ArtifactHash = z.string()
  .refine(art => isFixedHex(art, 16), "Expected name of exactly 16 hexits")

/** Zod schema request body for an artifact URL query. */
export const ArtifactsBody = z.array(ArtifactHash)

export const artifactsHandler = defineEventErrorHandler(async event => {
  validateMethod(event.method, ["POST"])
  const {owner, repo} = RepoParams.parse(getRouterParams(event, {decode: true}))
  const hashes = ArtifactsBody.parse(await readBody(event))
  return getArtifactUrls(`${owner}/${repo}`, hashes, isDev(event))
})

/** Zod schema for extracting an artifact hash from a `<hash>.art` artifact file name. */
export const ArtifactFromFile = z.string()
  .transform((art, ctx) => trimExt('art', art, ctx))
  .refine(art => isFixedHex(art, 16), "Expected name of exactly 16 hexits")

const GetArtifactParams = RepoParams.extend({
  artifact: ArtifactFromFile,
})

export const artifactHandler = defineEventErrorHandler(event => {
  validateMethod(event.method, ["GET"])
  const {owner, repo, artifact} = GetArtifactParams.parse(getRouterParams(event, {decode: true}))
  return getArtifact(`${owner}/${repo}`, artifact, isDev(event))
})

/**
 * Redirect to the location of a build output file in cloud storage.
 *
 * `repo`, `rev`, `platform`, and `toolchain` should have passed validation.
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

export const BuildOutputsQuery = z.object({
  rev: GitRev,
  platform: z.string().transform(validatePlatform).optional(),
  toolchain: z.string().transform(validateToolchain).optional(),
  dev: Dev,
})

export const outputsHandler = defineEventErrorHandler(event => {
  validateMethod(event.method, ["GET"])
  const {owner, repo} = RepoParams.parse(getRouterParams(event, {decode: true}))
  const {rev, platform, toolchain, dev} = BuildOutputsQuery.parse(getQuery(event))
  return getRevisionOutputs(`${owner}/${repo}`, rev, platform, toolchain, event.context.reservoir.dev || dev)
})
