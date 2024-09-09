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
    '@nuxtjs/seo',
    ['nuxt-svgo', {
      autoImportPath: false,
    }],
    ['@nuxtjs/critters', {
      config: {
        preload: "swap",
        pruneSource: true,
        reduceInlineStyles: false, // `true` breaks fonts
      }
    }],
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
      failOnError: false,
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
    failOnError: false,
    fetchRemoteUrls: false,
    skipInspections: ['link-text', 'absolute-site-urls'],
  },
  ogImage: {
    runtimeCacheStorage: false,
    fonts: [ 'Merriweather:400', 'Merriweather:700', 'Open+Sans:400' ],
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
