import { z } from 'zod'
import { getRouterParams, getQuery } from "h3"
import { validateMethod, defineEventErrorHandler } from '../utils/error'

export async function getBarrel(hash: string, dev: boolean) {
  const key = `${dev ? 'b0' : 'b1'}/${hash}.barrel`
  const url = `${process.env.S3_CDN_ENDPOINT}/${key}`
  return new Response(null, {status: 303, headers: {"Location": url}})
}

function parseBarrelExt(barrel: string, ctx: z.RefinementCtx) {
  const dotIdx = barrel.indexOf('.')
  if (dotIdx < 0) return barrel
  const ext = barrel.slice(dotIdx+1)
  if (ext == 'barrel') return barrel.slice(0, dotIdx)
  ctx.addIssue({
    code: z.ZodIssueCode.custom,
    message: `Expected file extension to be 'barrel', got '${ext}'`,
    fatal: true,
  });
  return z.NEVER
}

const GetBarrelParams = z.object({
  barrel: z.string().transform(parseBarrelExt)
    .refine(key => key.length == 64, "Expected name with exactly 64 hexits")
})

export const barrelHandler = defineEventErrorHandler(event => {
  validateMethod(event.method, ["GET"])
  const {barrel} = GetBarrelParams.parse(getRouterParams(event, {decode: true}))
  return getBarrel(barrel, getQuery(event).dev != undefined)
})
