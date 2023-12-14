import {packages, pkgLink} from './site/utils/manifest'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  srcDir: 'site',
  devtools: { enabled: true },
  typescript: { strict: true },
  build: {
    transpile: ['primevue'],
  },
  modules: [
    'unplugin-icons/nuxt',
    '@nuxtseo/module',
    ['nuxt-svgo', {
      autoImportPath: false,
    }],
    /*
    TODO: We presently monkey-match critters in `modules/critters.ts`
    to workaround a issue with Nuxt 3.8.2's new Nitro. We can switch back
    to this once that issue is resolved.
    ['@nuxtjs/critters', {
      config: {
        preload: "swap",
        pruneSource: true,
        reduceInlineStyles: false, // `true` breaks fonts
      }
    }],
    */
    ['@nuxtjs/google-fonts', {
      families: {
        'Merriweather': [400, 700],
        'Open+Sans': [400, 700],
        'Source+Code+Pro': [400],
      },
      display: 'swap',
      download: true,
    }],
  ],
  nitro: {
    prerender: {
      failOnError: true,
      autoSubfolderIndex: false,
      routes: ["/", ...packages.map(pkgLink)]
    },
  },
  site: {
    url: 'https://reservoir.lean-lang.org',
    name: 'Reservoir',
    description:
      "Reservoir is the package registry for Lake, the build system and " +
      "package manager of the Lean programming language and theorem prover.",
    titleSeparator: '|',
    defaultLocale: 'en-US',
  },
  linkChecker: {
    failOnError: true,
    fetchRemoteUrls: false,
  },
  ogImage: {
    runtimeCacheStorage: false,
    // Since Satori does not support multiple fonts, we exclude Open Sans.
    fonts: [ 'Merriweather:400', 'Merriweather:700' /* , 'Open+Sans:400' */ ],
  },
  vite: {
    build: {
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (id.includes('mathjax')) {
              return 'mathjax';
            }
          }
        }
      }
    }
  }
})
