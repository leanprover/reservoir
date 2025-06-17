<script setup lang="ts">
useHead({
  link: [
    { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
    { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
  ]
})

const site = useSiteConfig()
defineOgImageComponent('Generic', {
  title: site.name,
  description: site.description,
})
</script>

<template>
  <div class="app">
    <NuxtLayout>
      <NuxtPage/>
    </NuxtLayout>
  </div>
</template>

<style lang="scss">
@import url("normalize.css");
@import url('tippy.js/dist/tippy.css');

// palette is variants of slate and blue gray
:root {
  --light-color: #f9fbfd;
  --medium-color: #ebedf1;
  --dark-color: #1C74C1;
  --dark-accent-color: #6699cc;
  --light-accent-color: #a1c0e0;
  --light-text-color: white;
  --dark-text-color: black;
  --success-color: rgb(26, 127, 55);
  --warning-color: rgb(184, 134, 11);
  --failure-color: rgb(209, 36, 47);
  --neutral-color: var(--dark-color);

  --main-bg-color: var(--light-color);
  --main-text-color: var(--dark-text-color);
  --gutter-bg-color: var(--dark-color);
  --gutter-text-color: var(--light-text-color);
  --gutter-accent-color: var(--light-accent-color);
  --outcome-icon-color: var(--light-text-color);
  --card-bg-color: white;
  --star-color: gold;


    /* Typography */
    --font-primary: 'Open Sans', Arial, sans-serif;
    --font-secondary: 'Oranienbaum', serif;
    --fs-xs: 0.75rem;
    --fs-sm: 0.875rem;
    --fs-base: 1rem;
    --fs-md: 1.1rem;
    --fs-lg: 1.25rem;
    --fs-xl: 2rem;
    --fs-2xl: 3.3rem;

    /* Spacing (4px scale) */
    --space-1: 0.25rem;
    --space-2: 0.5rem;
    --space-3: 0.75rem;
    --space-4: 1rem;
    --space-5: 1.25rem;
    --space-6: 1.5rem;
    --space-8: 2rem;
    --space-10: 2.5rem;
    --space-12: 3rem;
    --space-13: 3.5rem;
    --space-14: 4rem;
    --space-16: 5rem;

    /* Semantic spacing */
    --gap-sm: var(--space-2);
    --gap-md: 10px;
    --gap-lg: 30px;
    --gap-xl: 100px;

    /* Section padding */
    --section-padding: var(--space-10);
    --section-padding-top: var(--space-16);

    /* Border Radius */
    --radius-sm: 0.25rem;
    --radius-md: 0.5rem;
    --radius-lg: 1rem;
    --radius-pill: 9999px;

    /* Sizes */
    --container-width: 1240px;
    --logo-size: 1.25rem;
    --logo-footer-size: 60px;
    --icon-size: 64px;

    /* Layout */
    --nav-padding-y: var(--space-6);
    --nav-padding-x: 10vw;
    --nav-height: calc(var(--nav-padding-y) * 2 + 3em);

    /* Transitions */
    --transition-fast: 0.2s;
    --transition-base: 0.3s;
    --transition-slow: 0.6s;
    --transition-delay-none: 0s;
    --transition-delay-small: 0.05s;
    --transition-delay-medium: 0.1s;
    --transition-delay-large: 0.15s;

    /* Animation */
    --animation-delay: 10000ms;

    /* Z-Index */
    --z-below: -1;
    --z-normal: 0;
    --z-above: 1;
    --z-header: 1000;

    /* Colors */
    --color-surface: #fff;
    --color-primary: #1C74C1;
    --color-primary-focus: #1763a5;
    --color-primary-light: #4a90e2;
    --color-secondary: #607D8B;
    --color-text: #333;
    --color-text-contrast: white;
    --color-text-light: #64748b;
    --color-muted: #607D8B;
    --color-bg: #F9FBFD;
    --color-bg-translucent: rgba(249, 251, 253, 0.81);
    --color-white: #fff;
    --color-border: #E4EBF3;
    --color-border-light: #D1D9E2;
    --color-hover: rgba(56, 110, 224, 0.08);
    --color-link-hover: #0073e6;
    --color-link-hover: #0073e6;
    --color-shadow: rgba(35, 55, 139, 0.1);

    /* Components */
    --btn-bg: var(--color-primary);
    --btn-text: var(--color-white);
    --btn-font: var(--font-primary);
    --btn-radius: var(--radius-md);

    /* Card specific */
    --card-bg: var(--color-white);
    --card-border: var(--color-border-light);

    /* Testimonial specific */
    --testimonial-bg: var(--color-primary);
    --testimonial-text: var(--color-white);
}

html, body {
  margin: 0;
  background-color: var(--main-bg-color);
}

h1, * {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

a {
  color: inherit;
  text-decoration: none;
  cursor: pointer;

  &.soft-link {
    &:hover, &:focus {
      color: var(--light-accent-color);
    }

    &:focus {
      outline: none;
    }
  }

  &.hard-link {
    color: var(--dark-accent-color);

    &:hover, &:focus {
      color: var(--light-accent-color);
    }

    &:focus {
      outline: none;
    }
  }
}

button {
  border: none;
  background-color: inherit;
}

.nowrap {
  white-space: nowrap
}

.tooltip {
  text-align: center;

  span.line {
    display: inline-block
  }
}

.icon {
  width: 1em;
  height: 1em;
  flex: 0 0 auto;

  &.prefix {
    margin-right: 0.5em;
  }

  &.suffix {
    margin-left: 0.5em;
  }
}

body {
  line-height: 1.2;
  font-family: 'Open Sans', sans-serif;
  min-height: 100vh;
}

code {
  font-family: 'Source Code Pro', monospace;
}

.card {
  border-radius: 5px;
  border: 1px solid var(--color-border);
  background-color: var(--card-bg-color);
}

header, main {
  display: flex;
  flex-direction: row;
  justify-content: center;

  & > .contents {
    flex-grow: 1;
    max-width: min(1080px, 100vw);
  }
}

.container {
  max-width: min(1080px, 100vw);
  width: 100%;
  margin: 0 auto;
}

.layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.gutter {
  background-color: var(--gutter-bg-color);
  color: var(--gutter-text-color);

  a {
    &:hover, &:focus {
      color: var(--gutter-accent-color);
    }

    &:focus {
      outline: none;
    }
  }
}

main {
  margin-top: var(--nav-height);
  flex-grow: 1;
  background-color: var(--main-bg-color);
  color: var(--main-text-color);

  & > .contents {
    padding: 1em;
    width: 100%;
  }
}

header {
  & > .contents {
    padding: 0.8em 1em;
  }

  .top-line {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;

    .search-bar {
      flex-grow: 1;
      margin-left: 1em;
      margin-right: 1em;
    }
  }
}

.page-header {
  margin-top: 3em;
  border-radius: 6px;
  margin-bottom: 1em;
}
</style>
