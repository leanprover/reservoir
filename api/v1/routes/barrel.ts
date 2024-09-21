import { defineEventHandler, getQuery } from "h3"
import { GetObjectCommand, NoSuchKey, S3Client } from "@aws-sdk/client-s3"
import { mkError } from '../utils/error'

export const barrelHandler = defineEventHandler(async (event) => {
  // Normalize key
  let key = event.context.params?.key
  if (!key) {
    return mkError(400, "Missing barrel name")
  }
  const ext = ".barrel"
  if (!key.endsWith(ext)) {
    key = key + ext
  }
  if (key.length != 64 + ext.length) {
    return mkError(400, "Invalid barrel name: should be exactly 64 hexits")
  }
  const dev = getQuery(event).dev != undefined
  key = `${dev ? 'dev' : 'b1'}/${key}`
  // Configure S3 client
  const endpoint = process.env.S3_ENDPOINT
  const accessKeyId = process.env.S3_ACCESS_KEY_ID
  const secretAccessKey = process.env.S3_SECRET_ACCESS_KEY
  if (!(endpoint && accessKeyId && secretAccessKey)) {
    console.error("No cloud storage configured")
    return mkError(404, "Barrel not found")
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
    console.log(`Get barrel ${key}`)
    const resp = await s3.send(new GetObjectCommand({
      Bucket: endpointConfig.bucket,
      Key: key,
    }))
    if (!resp.Body) {
      console.error("Barrel was empty")
      return mkError(404, "Barrel not found")
    }
    const headers: Record<string, string> = {
      "Content-Type": "application/vnd.reservoir.barrel+gzip"
    }
    if (resp.ContentLength) headers['Content-Length'] = resp.ContentLength?.toString()
    return new Response(resp.Body!.transformToWebStream(), {headers})
  } catch (e) {
    if (e instanceof NoSuchKey) {
      return mkError(404, "Barrel not found")
    } else {
      console.error(`Failed to retrieve barrel: ${e}`)
      return mkError(500, "Failed to retrieve barrel")
    }
  }
})
