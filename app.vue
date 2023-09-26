<script setup lang="ts">
useHead({
  htmlAttrs: {
    lang: 'en'
  },
  title: 'Reservoir',
  meta: [
    { name: 'description', content: 'The Lean package repository.' }
  ],
  link: [
    { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
  ]
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
  --medium-color: #bac3cb;
  --dark-color: #708090;
  --dark-accent-color: #6699cc;
  --light-accent-color: #a1c0e0;
  --light-text-color: white;
  --dark-text-color: black;
  --success-color: rgb(26, 127, 55);
  --failure-color: rgb(209, 36, 47);
  --neutral-color: var(--dark-color);

  --main-bg-color: var(--light-color);
  --main-text-color: var(--dark-text-color);
  --header-bg-color: var(--dark-color);
  --header-text-color: var(--light-text-color);
  --header-accent-color: var(--light-accent-color);
  --outcome-icon-color: var(--light-text-color);
  --card-bg-color: white;
  --star-color: gold;
}

html, body {
  margin: 0;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

a {
  color: inherit;
  text-decoration: none;
}

body {
  line-height: 1.2;
  background-color: var(--header-bg-color);
  font-family: 'Open Sans', sans-serif;
  min-height: 100vh;
}

h1, h2, h3, h4, h5, h6 {
  font-family: 'Merriweather', serif;
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
    max-width: 1080px;
    margin: 1em;
  }
}

header, footer {
  background-color: var(--header-bg-color);
  color: var(--header-text-color);
}

main {
  background-color: var(--main-bg-color);
  color: var(--main-text-color)
}

header > .contents {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;

  h1.title {
    margin: 0;
  }

  nav {
    a:hover {
      color: var(--light-accent-color);
    }

    .all {
      display: flex;
      flex-direction: row;
      align-items: center;

      .label {
        @media only screen and (max-width: 400px) {
          display: none;
        }
      }

      .icon {
        height: 1.5em;
        width: 1.5em;
        margin-left: 0.8em;
      }
    }
  }
}

footer > .contents {
  display: flex;
  margin: 0.5em 2em 3em 1.5em;

  @media only screen and (max-width: 700px) {
    flex-direction: column;
    justify-content: space-between;
  }

  @media screen and (min-width: 700px) {
    flex-direction: row;
    justify-content: space-around;
  }

  ul {
    list-style: none;
    color: var(--header-color);

    li {
      display: flex;
      align-items: center;

      padding: 0.3em 0;
      line-height: 1em;

      a {
        color: var(--header-text-color);

        .icon {
          width: 1em;
          height: 1em;
          margin-right: 0.5em;
        }

        &:hover {
          color: var(--header-accent-color);
        }
      }
    }
  }

  h2 {
    margin-top: 1em;
    margin-bottom: 0.5em;
    color: var(--header-accent-color);
  }
}
</style>
