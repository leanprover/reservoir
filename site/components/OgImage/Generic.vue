<script setup lang="ts">
// @ts-ignore (custom.d.ts does not apply here for some reason)
import LogoIcon from '~/public/favicon.svg?component'
import type { CSSProperties } from 'vue'

// inherited attrs can mess up the satori parser
defineOptions({
  inheritAttrs: false,
})

const siteTitle = useSiteConfig().name
const props = defineProps<{
  title: string
  description?: string
  hasNoDescription?: boolean
}>()

// cannot use `!pkg.description` because a falsy description
// will just fallback to the application-wide site description
const hasDescription = !props.hasNoDescription

const mainStyles: CSSProperties = {
  width: '100%',
  height: '100%',
  backgroundColor: '#f9fbfd',
  boxSizing: 'border-box',
  borderBottom: '2em solid #708090',
  padding: '0 3em',
  display: 'flex',
  flexDirection: 'column',
}

const articleStyles: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  flexGrow: '1',
  minHeight: '0',
  overflow: 'hidden',
}

const textStyles: CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
}

const titleStyles: CSSProperties = {
  margin: "0.5em 0",
  fontSize: "5em",
  fontWeight: "bold",
  overflow: "hidden",
  textOverflow: "ellipsis",
  whiteSpace: "nowrap"
}

const descrStyles: CSSProperties = {
  display: 'block',
  fontSize: "3em",
  // Currently (as of 01-2024), this does not actually do anything,
  // as the Satori renderer does not support multiple embedded font families.
  // This is simply a reminder for whenever it might in the future.
  fontFamily: "'Open Sans', sans-serif",
  lineClamp: 5,
}

const footerStyles: CSSProperties = {
  display: "flex",
  justifyContent: "flex-end",
  alignItems: "baseline",
  fontSize: "2em",
  height: "1.2em",
  marginBottom: "1em",
  marginTop: "0.5em"
}

const siteTitleStyles: CSSProperties = {
  display: props.title == siteTitle ? "none" : "flex",
  fontFamily: "'Merriweather', serif"
}

const iconStyles: CSSProperties = {
  fontSize: "1.25em",
  width: "1em",
  height: "1em",
  marginLeft: "0.5em"
}
</script>

<template>
  <main :style="mainStyles">
    <article :style="articleStyles">
      <div :style="textStyles">
        <div :style="titleStyles">{{ props.title }}</div>
        <div :style="descrStyles" v-if="hasDescription">{{ props.description }}</div>
      </div>
    </article>
    <footer :style="footerStyles">
      <div :style="siteTitleStyles">{{ siteTitle }}</div>
      <LogoIcon :style="iconStyles"/>
    </footer>
  </main>
</template>

<style lang="scss">
* {
  box-sizing: "border-box";
}
</style>
