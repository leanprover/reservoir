<script setup lang="ts">
const props = defineProps<{package: Package}>()
const pkg = computed(() => props.package)
</script>

<template>
  <div class="versions-tab">
    <ol class="item-list">
      <VersionItem v-for="ver in pkg.versions" :key="ver.revision" :pkg="pkg" :ver="ver"/>
    </ol>
  </div>
</template>
