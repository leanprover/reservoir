/*
Adapted from  https://github.com/juliomrqz/nuxt-netlify by Julio Marquez
Ported to Nuxt 3 and TypeScript

---

Copyright (c) 2020 Julio Marquez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

import path from 'path'
import fs from 'fs-extra'
import {defineNuxtModule, logger} from 'nuxt/kit'

export interface Redirect {
  from: string
  to: string
  status?: number
  force?: boolean
  query?: {
    [key: string]: string
  }
  conditions?: {
    [key: string]: string[]
  } & {
    Language?: string[]
    Country?: string[]
    Role?: string[]
    Cookie?: string[]
  }
}

export const isEmptyObject = (o: object) => Object.keys(o).length === 0

export const createRedirectContent = (redirect: Redirect) => {
  const divider = '    '

  // from
  let content = `${redirect.from}${divider}`

  // query params
  if (redirect.query && !isEmptyObject(redirect.query)) {
    content += Object.entries(redirect.query)
      .map(([k,v]) => `${k}=${v}`)
      .join('  ')
    content += divider
  }

  // to
  content += `${redirect.to}${divider}`

  // status
  if (redirect.status || redirect.force) {
    content += `${redirect.status ?? 301}${redirect.force ? '!' : ''}`
  }

  // conditions
  if (redirect.conditions && !isEmptyObject(redirect.conditions)) {
    content += divider
    content += Object.entries(redirect.conditions)
      .map(([k,vs]) => `${k}=${vs.join(',')}`)
      .join('  ')
  }
  return `${content}\n`
}

export const createFile = async (filePath: string, content: string) => {
  if (await fs.exists(filePath)) {
    await fs.appendFile(filePath, `\n\n${content}`)
  } else {
    await fs.ensureFile(filePath)
    await fs.writeFile(filePath, content)
  }
}

export const defineRedirectsModule = (redirects?: Redirect[]) => defineNuxtModule({
  meta: {
    name: 'redirects'
  },
  hooks: {
    'nitro:build:public-assets': async nitro => {
      try {
        const filePath = path.resolve(nitro.options.output.publicDir, '_redirects')
        const content = (redirects ? redirects.reduce((c, r) => c + createRedirectContent(r), "") : "")
        await createFile(filePath, content)
        logger.success('Generated _redirects')
      } catch (error) {
        logger.error(error)
      }
    }
  }
})
