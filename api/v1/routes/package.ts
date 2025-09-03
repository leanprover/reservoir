import { z } from 'zod'
import { createRouter, getRouterParams, getQuery } from 'h3'
import { InternalServerError, defineEventErrorHandler, NotFound, validateMethod } from '../utils/error'
import { getBarrel } from '../routes/barrel'
import { parseArtifact, getArtifact } from '../routes/artifact'
import type { Build } from '../../../site/utils/manifest'

/**
 * Fetch JSON data for the package `<owner>/<name>`
 * stored at `<filePath>.json` in the index at `indexUrl`.
 *
 * `owner` and `path` should be URL encoded.
 */
async function fetchPackageJson(indexUrl: string, owner: string, name: string, filePath: string) {
  const fileUrl = `${indexUrl}/${owner.toLowerCase()}/${name.toLowerCase()}/${filePath}.json`
  console.log(`Fetch ${fileUrl}`)
  const res = await fetch(fileUrl)
  if (res.status == 200) {
    return new Response(res.body, {
      headers: {"Content-Type": "application/json; charset=utf-8"}
    })
  } else if (res.status == 404) {
    console.log("Package not found")
    throw new NotFound("Package not found in index")
  } else {
    console.error(`Fetch failed (${res.status}): ${await res.text}`)
    throw new InternalServerError("Failed to retrieve package data from index")
  }
}

const PackageParams = z.object({
  name: z.string().min(1),
  owner: z.string().min(1),
})

export const packageRouter = createRouter()

packageRouter.use('/packages/:owner/:name', defineEventErrorHandler(event => {
  validateMethod(event.method, ["GET"])
  const {owner, name} = PackageParams.parse(getRouterParams(event))
  return fetchPackageJson(event.context.reservoir.indexUrl, owner, name, 'metadata')
}))

packageRouter.use('/packages/:owner/:name/builds', defineEventErrorHandler(event => {
  validateMethod(event.method, ["GET"])
  const {owner, name} = PackageParams.parse(getRouterParams(event))
  return fetchPackageJson(event.context.reservoir.indexUrl, owner, name, 'builds')
}))

packageRouter.use('/packages/:owner/:name/versions', defineEventErrorHandler(event => {
  validateMethod(event.method, ["GET"])
  const {owner, name} = PackageParams.parse(getRouterParams(event))
  return fetchPackageJson(event.context.reservoir.indexUrl, owner, name, 'versions')
}))

function normalizeToolchain(toolchain: string): string {
  let origin, ver
  const colonIdx = toolchain.indexOf(':')
  if (colonIdx < 0) {
    origin = "leanprover/lean4"
    ver = toolchain
  } else {
    origin = toolchain.slice(0, colonIdx)
    ver = toolchain.slice(colonIdx+1)
  }
  if (ver[0] >= '0' && ver[0] <= '9') {
    ver = `v${ver}`
  }
  return `${origin}:${ver}`
}

const PackageBarrelQuery = z.object({
  rev: z.string().refine(rev => rev.length == 40, "Expected revision of exactly 40 hexits").optional(),
  toolchain: z.string().transform(normalizeToolchain).optional(),
  dev: z.any().optional().transform(dev => dev != undefined),
})

packageRouter.use('/packages/:owner/:name/barrel', defineEventErrorHandler(async event => {
  validateMethod(event.method, ["GET"])
  const {owner, name} = PackageParams.parse(getRouterParams(event))
  const {rev, toolchain, dev} = PackageBarrelQuery.parse(getQuery(event))
  console.log(`Looking for barrel for '${owner}/${name}' at '${rev?.slice(0, 7)}' on '${toolchain}'`)
  const res = await fetchPackageJson(event.context.reservoir.indexUrl, owner, name, 'builds')
  const builds: Build[] = (await res.json())['data']
  const hash = builds.find(build => {
    if (!build.archiveHash) return false
    if (rev && build.revision != rev) return false
    if (toolchain && build.toolchain != toolchain) return false
    return true
  })?.archiveHash
  if (!hash) {
    throw new NotFound("No barrel found that satisfies criteria")
  }
  return getBarrel(hash, dev)
}))

const PackageArtifactParams = PackageParams.extend({
  artifact: z.string().transform(parseArtifact),
})

const PackageArtifactQuery = z.object({
  dev: z.any().optional().transform(dev => dev != undefined),
})

packageRouter.use('/packages/:owner/:name/artifacts/:artifact', defineEventErrorHandler(async event => {
  validateMethod(event.method, ["GET"])
  const {owner, name, artifact} = PackageArtifactParams.parse(getRouterParams(event))
  const {dev} = PackageArtifactQuery.parse(getQuery(event))
  const res = await fetchPackageJson(event.context.reservoir.indexUrl, owner, name, 'metadata')
  const sources: Source[] = (await res.json())['sources']
  const githubSrc = sources.find(src => src['host'] == 'github')
  if (githubSrc) {
    return getArtifact(githubSrc.fullName, artifact, dev)
  } else {
    console.log("Package lacks a GitHub source")
    throw new NotFound("Package lacks artifacts")
  }
}))
