<script setup lang="ts">
const props = defineProps<{package: Package}>()
const deps = computed(() => props.package.dependents)
</script>

<template>
  <div class="dependents-tab">
    <ol class="item-list">
      <DepItem :upstream="false" v-for="dep in deps" :key="dep.name" :dep="dep"/>
    </ol>
  </div>
</template>
