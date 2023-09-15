<script setup lang="ts">
import manifest from '~/manifest.json'
</script>

<template>
  <header>
    <h1 class="title">Reservoir</h1>
  </header>
  <main v-if="manifest !== null">
    <div class="toolchain">
      <span class="label">Latest Toolchain: </span>
      <span class="name">{{ manifest.toolchain }}</span>
    </div>
    <h2>Build Status of {{ manifest.matrix.length }} of the Top Repositories</h2>
    <ol class="matrix">
      <li v-for="repo in manifest.matrix" :class="'outcome-' +  repo.outcome">
        <a :href="repo.url">{{ repo.fullName }}</a>
      </li>
    </ol>
  </main>
  <main v-else>
    <p>Oops! Build data for the repositories is missing.</p>
  </main>
</template>

<style lang="scss">
@import url("https://unpkg.com/ionicons@4.5.10-0/dist/css/ionicons.min.css");
@import url('https://fonts.googleapis.com/css2?family=Merriweather&family=Open+Sans&family=Source+Code+Pro&family=Source+Code+Pro:wght@600&display=swap');

html {
  --main-bg: white;
  --header-bg: #f8f8f8;
  --link-color: hsl(210, 100%, 30%);
  --success-color: rgb(26, 127, 55);
  --failure-color: rgb(209, 36, 47);
}

a {
  color: var(--link-color);
  text-decoration: none;
}

body {
  font-family: 'Open Sans', sans-serif;
  background-color: var(--header-bg);
  padding: 0;
  margin: 0;
}

h1, h2, h3, h4, h5, h6 {
  font-family: 'Merriweather', serif;
}

header {
  height: 3.5em;
  text-align: center;
  background-color: #f8f8f8;
}

main {
  margin: 0 1.5em;
  padding: 1.5em;
  background-color: var(--main-bg);
}

.toolchain {
  font-size: larger;
  & > .label {
    font-weight: bold;
  }
  & > .name {
    font-size: 1em;
  }
}

.matrix {
  counter-reset: item;
  li {
    display: block;
    font-size: larger;

    &.outcome-success::before {
      content: ""; // .ion-ios-checkmark
      background-color: var(--success-color);
    }

    &.outcome-failure::before {
      content: ""; // .ion-ios-close
      background-color: var(--failure-color);
    }

    &::before {
      font-family: "Ionicons";
      color: white;
      text-align: center;
      border-radius: 50%;
      display: inline-block;
      content: counter(item) ") ";
      counter-increment: item;
      width: 1em;
      height: 1em;
      line-height: 1em;
      margin-right: 0.5em;
      margin-left: -2em;
      margin-bottom: 0.5em;
    }
  }
}
</style>
