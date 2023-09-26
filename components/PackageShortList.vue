<script setup lang="ts">
const props = defineProps<{pkgs: any[]}>()
</script>

<template>
  <ol class="short-list">
    <li class="card" v-for="pkg in props.pkgs" :key="pkg.id">
      <BuildOutcome class="icon" :outcome="pkg.outcome"/>
      <a :href="pkg.url">{{ pkg.name }}</a>
    </li>
  </ol>
</template>

<style scoped lang="scss">
.short-list {
  list-style: none;

  li {
    display: flex;
    flex-direction: row;
    align-items: center;
    margin: 0 0 0.8em 0;
    padding: 1em;

    .icon {
      width: 1.2em;
      height: 1.2em;
      margin-right: 0.7em;
    }

    a {
      overflow: hidden;
      text-overflow: ellipsis;

      &:hover {
        color: var(--dark-accent-color);
      }
    }
  }
}
</style>
