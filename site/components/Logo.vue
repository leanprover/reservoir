<script setup lang="ts">
import LogoIcon from '~/public/favicon.svg?component'
</script>

<template>
  <NuxtLink aria-label="Reservoir" class="logo" to="/">
    <LogoIcon class="icon"/>
    <h1 class="label">Reservoir</h1>
  </NuxtLink>
</template>

<style scoped lang="scss">
.logo {
  display: flex;
  align-items: center;
  font-size: 1.8em;

  &.compact {
    @media only screen and (max-width: 600px) {
      .label { display: none; }
    }
  }

  .label {
    font-size: inherit;
    margin-left: 0.5em;
  }

  .icon {
    height: 1.5em;
    width: 1.5em;
  }
}
</style>
