import manifest from './site/manifest.json'
import { defineNuxtConfig } from 'nuxt/config'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  srcDir: 'site',
  devtools: { enabled: true },
  typescript: { strict: true },
  build: {
    transpile: ['primevue']
  },
  modules: [
    'unplugin-icons/nuxt',
    ['nuxt-svgo', {
      autoImportPath: false,
    }],
    ['@nuxtjs/critters', {
      config: {
        preload: "body",
        pruneSource: true,
        reduceInlineStyles: false, // `true` breaks fonts
      }
    }],
    ['@nuxtjs/google-fonts', {
      families: {
        Merriweather: [400],
        'Open+Sans': [400],
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
      routes: ["/", ...manifest.matrix.map((pkg) => `/packages/${pkg.id}`)]
    },
  },
})
