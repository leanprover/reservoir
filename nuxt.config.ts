import manifest from './manifest.json'
import { defineNuxtConfig } from 'nuxt/config'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: false },
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
        // 'Source+Code+Pro': [400, 600],
      },
      display: 'swap',
      download: true,
    }],
  ],
  nitro: {
    prerender: {
      failOnError: true,
      routes: ["/", ...manifest.matrix.map((pkg) => `/packages/${pkg.id}`)]
    },
  },
})
