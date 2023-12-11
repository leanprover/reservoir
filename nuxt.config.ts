import pkgLink from './site/utils/pkgLink'
import {packages} from './site/utils/manifest'

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
      failOnError: true,
      // Needed to prevent GitHub Pages from automatically adding trailing
      // slashes to URLs (as otherwise they are directories rather than files)
      autoSubfolderIndex: false,
      routes: ["/", ...packages.map(pkgLink)]
    },
  },
  site: {
    url: 'https://reservoir.lean-lang.org',
    name: 'Reservoir',
    description: "Lake's package registry for the Lean community.",
    titleSeparator: '|',
    defaultLocale: 'en-US',
  },
  linkChecker: {
    failOnError: true,
    fetchRemoteUrls: false,
  },
  ogImage: {
    defaults: {
      cache: false,
      component: 'OgImageGeneric',
    },
    runtimeBrowser: false,
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
