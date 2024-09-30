import { z } from 'zod'
import { getRouterParams, getQuery } from "h3"
import { GetObjectCommand, NoSuchKey, S3Client, S3ServiceException } from "@aws-sdk/client-s3"
import { NotFound, InternalServerError, validateMethod, defineEventErrorHandler } from '../utils/error'

export async function getBarrel(hash: string, dev: boolean, name?: string) {
  const key = `${dev ? 'dev' : 'b1'}/${hash}.barrel`
  // Configure S3 client
  const endpoint = process.env.S3_ENDPOINT
  const accessKeyId = process.env.S3_ACCESS_KEY_ID
  const secretAccessKey = process.env.S3_SECRET_ACCESS_KEY
  if (!(endpoint && accessKeyId && secretAccessKey)) {
    console.error("No cloud storage configured")
    throw new NotFound("Barrel not found")
  }
  const endpointUrl = new URL(endpoint)
  const endpointConfig =
    endpointUrl.pathname == "/" ? {
      endpoint: undefined,
      bucket: endpointUrl.origin,
      bucketEndpoint: true,
    } : {
      endpoint: endpointUrl.origin,
      bucket: endpointUrl.pathname.slice(1),
      bucketEndpoint: false,
    }
  const s3 = new S3Client({
    region: 'auto',
    endpoint: endpointConfig.endpoint,
    bucketEndpoint: endpointConfig.bucketEndpoint,
    credentials: {
      accessKeyId: accessKeyId,
      secretAccessKey: secretAccessKey,
    },
  })
  // Fetch barrel
  try {
    console.log(`S3 GetObject ${key}`)
    const resp = await s3.send(new GetObjectCommand({
      Bucket: endpointConfig.bucket,
      Key: key,
    }))
    if (!resp.Body) {
      console.error("Barrel was empty")
      throw new NotFound("Barrel not found")
    }
    const headers: Record<string, string> = {
      "Content-Type": "application/vnd.reservoir.barrel+gzip",
      "Content-Disposition": `attachment; filename=${name ?? hash}.barrel`
    }
    if (resp.ContentLength) headers['Content-Length'] = resp.ContentLength?.toString()
    return new Response(resp.Body!.transformToWebStream(), {headers})
  } catch (e) {
    if (e instanceof NoSuchKey) {
      console.log("Barrel not found")
      throw new NotFound("Barrel not found", {cause: e})
    } else if (e instanceof S3ServiceException) {
      console.error(`Failed to retrieve barrel: ${e}`)
      throw new InternalServerError("Failed to retrieve barrel", {cause: e})
    }
  }
}

export function parseBarrelExt(barrel: string, ctx: z.RefinementCtx) {
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

export const GetBarrelParams = z.object({
  barrel: z.string().transform(parseBarrelExt)
    .refine(key => key.length == 64, "Expected name with exactly 64 hexits")
})

export const barrelHandler = defineEventErrorHandler(event => {
  validateMethod(event.method, ["GET"])
  const {barrel} = GetBarrelParams.parse(getRouterParams(event, {decode: true}))
  return getBarrel(barrel, getQuery(event).dev != undefined)
})
