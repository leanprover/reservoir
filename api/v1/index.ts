import { type Config } from "@netlify/functions"
import { createApp, createRouter, useBase } from "h3"
import { packageRouter } from './routes/package'
import { barrelHandler } from './routes/barrel'
import { artifactHandler } from './routes/artifact'
import { toNetlifyHandler } from "./utils/netlify"
import { mkError } from './utils/error'
import { initReservoirContext } from "./utils/reservoir"

const app = createApp({
  onRequest: async event => {
    initReservoirContext(event)
  },
  onError: async (error, event) => {
    await event.respondWith(mkError(error.statusCode, error.statusMessage ?? '', event.headers))
  },
})

const v1 = createRouter()

v1.use("**", packageRouter.handler)
v1.use("/barrels/:barrel", barrelHandler)
v1.use("/artifacts/:artifact", artifactHandler)

app.use("/api/v1", useBase("/api/v1", v1.handler))
app.use("/api/v0", useBase("/api/v0", v1.handler))

export const config: Config = {
  path: "/api/**"
}

export default toNetlifyHandler(app)
