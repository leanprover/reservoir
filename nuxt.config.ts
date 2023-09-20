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
  ],
})
