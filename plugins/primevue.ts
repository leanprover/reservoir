import PrimeVue from 'primevue/config'
import { defineNuxtPlugin } from 'nuxt/app'

export default defineNuxtPlugin(nuxtApp => {
  nuxtApp.vueApp.use(PrimeVue, { unstyled: true })
})
