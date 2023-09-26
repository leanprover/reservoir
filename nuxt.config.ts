import { defineNuxtConfig } from 'nuxt/config'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: false },
  typescript: { strict: true },
  experimental: {
    watcher: "parcel",
  },
  modules: [
    'unplugin-icons/nuxt',
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
    },
  },
})
