<script setup lang="ts">
const props = defineProps<{package: Package}>()
const deps = computed(() => props.package.versions.at(0)?.dependencies ?? [])
</script>

<template>
  <div class="versions-tab">
    <ol class="item-list">
      <DepItem :upstream="true" v-for="dep in deps" :key="dep.name" :dep="dep"/>
    </ol>
  </div>
</template>
