import { z } from 'zod'
import { createRouter, getRouterParams, getQuery } from 'h3'
import { InternalServerError, defineEventErrorHandler, NotFound, validateMethod } from '../utils/error'
import { getBarrel, parseBarrelExt } from '../routes/barrel'
import type { Build } from '../../../site/utils/manifest'

/**
 * Fetch JSON data for the package `<owner>/<name>`
 * stored at `<filePath>.json` in the index at `indexUrl`.
 *
 * `owner` and `path` should be URL encoded.
 */
export async function fetchPackageJson(indexUrl: string, owner: string, name: string, filePath: string) {
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

export const PackageParams = z.object({
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

const PackageGetBarrelParams = PackageParams.extend({
  barrelRev: z.string().transform(parseBarrelExt)
    .refine(rev => rev.length == 40, "Expected revision of exactly 40 hexits")
})

packageRouter.use('/packages/:owner/:name/barrels/:barrelRev', defineEventErrorHandler(async event => {
  validateMethod(event.method, ["GET"])
  const {owner, name, barrelRev} = PackageGetBarrelParams.parse(getRouterParams(event))
  const res = await fetchPackageJson(event.context.reservoir.indexUrl, owner, name, 'builds')
  const builds: Build[] = (await res.json())['data']
  const hash = builds.find(build => build.revision == barrelRev)?.archiveHash
  if (!hash) {
    throw new NotFound("Barrel not found for revision")
  }
  return getBarrel(hash, getQuery(event).dev != undefined, barrelRev)
}))
