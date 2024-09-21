import { type Config } from "@netlify/functions"
import { createApp, createRouter, useBase } from "h3"
import { packageHandler } from './routes/package'
import { fromNetlifyHandler, toNetlifyHandler } from "./utils/netlify"
import { mkError } from './utils/error'

const app = createApp({
  onError: async (error, event) => {
    await event.respondWith(mkError(error.statusCode, error.statusMessage ?? '', event.headers))
  },
})

const v1 = createRouter()

v1.use("/packages/:owner/:name", fromNetlifyHandler(packageHandler))

app.use("/api/v1", useBase("/api/v1", v1.handler))
app.use("/api/v0", useBase("/api/v0", v1.handler))

export const config: Config = {
  path: "/api/**"
}

export default toNetlifyHandler(app)
