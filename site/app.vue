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
  --dark-color: #708090;
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
}

html, body {
  margin: 0;
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

h1, h2, h3, h4, h5, h6 {
  font-family: 'Merriweather', serif;
}

code {
  font-family: 'Source Code Pro', monospace;
}

.card {
  border-radius: 12px;
  border-left: 1px solid var(--light-accent-color);
  border-bottom: 1px solid var(--light-accent-color);
  background-color: var(--card-bg-color);
}

header, main, footer {
  display: flex;
  flex-direction: row;
  justify-content: center;

  & > .contents {
    flex-grow: 1;
    max-width: min(1080px, 100vw);
  }
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
  flex-grow: 1;
  background-color: var(--main-bg-color);
  color: var(--main-text-color);

  & > .contents {
    padding: 1em;
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
  padding: 1em;
  background-color: var(--medium-color);
  border-radius: 6px;
  margin-bottom: 1em;
}
</style>
