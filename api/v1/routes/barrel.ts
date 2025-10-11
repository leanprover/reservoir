import { z } from 'zod'
import { getRouterParams, getQuery } from "h3"
import { validateMethod, defineEventErrorHandler } from '../utils/error'
import { trimExt, isFixedHex } from '../utils/zod'

/**
 * Redirect to the location of an barrel in cloud storage.
 *
 * `hash` should have passed validation.
 */
export async function getBarrel(hash: string, dev: boolean) {
  const key = `${dev ? 'b0' : 'b1'}/${hash}.barrel`
  const url = `${process.env.S3_CDN_ENDPOINT}/${key}`
  return new Response(null, {status: 303, headers: {"Location": url}})
}

/** Zod schema for extracting a barrel hash from a `<hash>.barrel` file name. */
export const BarrelFromFile = z.string()
  .transform((name, ctx) => trimExt('barrel', name, ctx))
  .refine(key => isFixedHex(key, 64), "Expected name with exactly 64 hexits")

const GetBarrelParams = z.object({
  barrel: BarrelFromFile
})

export const barrelHandler = defineEventErrorHandler(event => {
  validateMethod(event.method, ["GET"])
  const {barrel} = GetBarrelParams.parse(getRouterParams(event, {decode: true}))
  const dev = event.context.reservoir.dev || getQuery(event).dev != undefined
  return getBarrel(barrel, dev)
})
