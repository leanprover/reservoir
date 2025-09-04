import { z } from 'zod'
import { getRouterParams, getQuery } from "h3"
import { validateMethod, defineEventErrorHandler } from '../utils/error'
import { trimExt } from '../utils/zod'

export async function getArtifact(scope: string, hash: string, dev: boolean) {
  const key = `${dev ? 'a0' : 'a1'}/${scope}/${hash}.art`
  const url = `${process.env.S3_CDN_ENDPOINT}/${key}`
  return new Response(null, {status: 303, headers: {"Location": url}})
}

/** Zod schema for extracting an artifact hash from a `<hash>.art` artifact file name. */
export const ArtifactFromFile = z.string()
  .transform((art, ctx) => trimExt('art', art, ctx))
  .refine(art => art.length == 16, "Expected name of exactly 16 hexits")

const GetArtifactParams = z.object({
  owner: z.string().min(1),
  repo: z.string().min(1),
  artifact: ArtifactFromFile,
})

export const artifactHandler = defineEventErrorHandler(event => {
  validateMethod(event.method, ["GET"])
  const {owner, repo, artifact} = GetArtifactParams.parse(getRouterParams(event, {decode: true}))
  const dev = event.context.reservoir.dev || getQuery(event).dev != undefined
  return getArtifact(`${owner}/${repo}`, artifact, dev)
})

export async function getRevisionOutputs(scope: string, rev: string, dev: boolean) {
  const key = `${dev ? 'a0' : 'a1'}/${scope}/${rev}.art`
  const url = `${process.env.S3_CDN_ENDPOINT}/${key}`
  return new Response(null, {status: 303, headers: {"Location": url}})
}

/** Zod schema for extracting a Git revision from a `<rev>.jsonl` outputs file name. */
export const RevisionFromOutputsFile = z.string()
  .transform((rev, ctx) => trimExt('jsonl', rev, ctx))
  .refine(rev => rev.length == 40, "Expected revision of exactly 40 hexits")

const GetOutputsParams = z.object({
  owner: z.string().min(1),
  repo: z.string().min(1),
  rev: RevisionFromOutputsFile,
})

export const outputsHandler = defineEventErrorHandler(event => {
  validateMethod(event.method, ["GET"])
  const {owner, repo, rev} = GetOutputsParams.parse(getRouterParams(event, {decode: true}))
  const dev = event.context.reservoir.dev || getQuery(event).dev != undefined
  return getRevisionOutputs(`${owner}/${repo}`, rev, dev)
})
