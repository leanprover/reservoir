<script setup lang="ts">
import LeakIcon from '~/assets/barrel-leak.svg?component'
const props = defineProps<{error: {
    url: string;
    statusCode: number;
    statusMessage: string;
    message: string;
    description: string;
    data?: any;
}}>();
</script>

<template>
  <NuxtLayout>
    <div class="error-page">
      <div class="icon">
        <LeakIcon style="height: 100%; width: 100%"/>
      </div>
      <h1 class="header">{{ props.error.statusMessage }}</h1>
      <div>Oops! It appears Reservoir sprung a leak!</div>
    </div>
  </NuxtLayout>
</template>

<style lang="scss">
.error-page {
  height: 100%;

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;

  .icon {
    height: auto;
    width: min(100%, 25em);
  }

  .header {
    margin: 0.8em 0 0.3em 0;
  }
}
</style>
