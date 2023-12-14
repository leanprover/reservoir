/*
Adapted from https://github.com/nuxt-modules/critters
Monkey-patched for Nuxt 3.8.2's new Nitro

---

MIT License

Copyright (c)

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
import Critters from 'critters'
import { defineNuxtModule } from '@nuxt/kit'

export default defineNuxtModule({
  meta: {
    name: 'critters',
  },
  setup (_, nuxt) {
    // Only enable for production
    if (nuxt.options.dev) return

    // Nitro handler (for prerendering only)
    nuxt.hook('nitro:init', nitro => {
      const critters = new Critters({
        /*
        With Nuxt 3.8.2's new Nitro, Nuxt's CSS files are not copied
        from this directory into `nitro.options.output.publicDir` until
        *after* this module's hook is run, thus we have to point Critters
        to this build directory instead.
        */
        path: path.resolve(nuxt.options.buildDir, 'dist/client'),
        publicPath: nitro.options.baseURL,
        preload: "swap",
        pruneSource: true,
        reduceInlineStyles: false, // `true` breaks fonts
      })
      nitro.hooks.hook('prerender:generate', async route => {
        if (!route.fileName?.endsWith('.html') || route.error || !route.contents) return
        route.contents = await critters.process(route.contents)
      })
    })
  }
})
