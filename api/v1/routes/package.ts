import { z } from 'zod'
import { getRouterParams } from 'h3'
import { InternalServerError, defineEventErrorHandler, NotFound, validateMethod } from '../utils/error'

/**
 * Fetch the package metadata for `<owner>/<name>` from the index at `baseUrl`.
 *
 * `owner` and `path` should be URL encoded.
 */
export async function getPackage(baseUrl: string, owner: string, name: string) {
  const path = `${owner.toLowerCase()}/${name.toLowerCase()}`
  const fileUrl = `${baseUrl}/${path}/metadata.json`
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

export const GetPackageParams = z.object({
  name: z.string().min(1),
  owner: z.string().min(1),
})

export const packageHandler = defineEventErrorHandler(event => {
  validateMethod(event.method, ["GET"])
  const {owner, name} = GetPackageParams.parse(getRouterParams(event))
  return getPackage(`${event.web!.url!.origin}/index`, owner, name)
})
