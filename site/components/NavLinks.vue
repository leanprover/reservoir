<script setup lang="ts">
import IndexIcon from '~icons/mdi/lake'
</script>

<template>
  <nav>
    <NuxtLink aria-label="All Packages" to="/packages" class="all">
      <span class="label">All Packages</span>
      <IndexIcon class="icon"/>
    </NuxtLink>
  </nav>
</template>

<style scoped lang="scss">
nav {
  &.compact {
    @media only screen and (max-width: 800px) {
      .label { display: none; }
    }
  }

  &:not(.compact) {
    @media only screen and (max-width: 600px) {
      .label { display: none; }
    }
  }

  .all {
    display: flex;
    flex-direction: row;
    align-items: center;

    .label {
      margin-right: 0.75em;
    }

    .icon {
      font-size: 1.5em;
    }
  }
}
</style>
