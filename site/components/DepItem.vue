<script setup lang="ts">
import GitIcon from '~icons/mdi/git'
import FolderIcon from '~icons/mdi/folder'
import UnknownIcon from '~icons/mdi/help'
import ReservoirIcon from '~/public/favicon.svg?component'
const props = defineProps<{dep: PackageDep, upstream: boolean}>()
const pkg = computed(() => props.dep.scope ? findPkg(props.dep.scope, props.dep.name) : undefined)
</script>

<template>
  <li class="dep-item card">
    <div v-if="upstream" class="dep-type">
      <ReservoirIcon v-if="pkg" class="icon"/>
      <GitIcon v-else-if="dep.type == 'git'" class="icon"/>
      <FolderIcon v-else-if="dep.type == 'path'" class="icon"/>
      <UnknownIcon v-else class="icon"/>
    </div>
    <div class="dep-info">
      <h3 class="dep-header">
        <NuxtLink class="dep-link" v-if="pkg" :to="pkgLink(pkg)">{{dep.name}}</NuxtLink>
        <span v-else>{{dep.name}}</span>
        <span class="dep-version">
          <span class="label">{{ upstream ? '@ ' : 'uses '  }}</span>
          <code>
            {{dep.version == '0.0.0' ? (dep.rev ? dep.rev.slice(0, 7) : dep.version) : dep.version}}
          </code>
        </span>
      </h3>
      <div v-if="pkg" class="description">
        {{ pkg.description  }}
      </div>
    </div>
  </li>
</template>

<style lang="scss">
li.dep-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  position: relative;
  padding: 1em 1.5em;

  &:has(.dep-link):hover {
    background-color: var(--medium-color);
  }

  &:has(.dep-link:focus) {
    border-width: 2px;
    border-color: var(--dark-color);
  }

  .dep-type {
    margin-right: 1.2em;

    .icon {
      width: 1.8em;
      height: 1.8em;
    }
  }

  .dep-header {
    display: flex;
    align-items: baseline
  }


  .dep-version {
    font-size: 0.8em;
    color: var(--dark-color);
    margin-left: 0.5rem;
  }

  .dep-link {
    &:focus {
      outline: none;
    }

    &::after {
      content: '';
      position: absolute;
      left: 0;
      right: 0;
      bottom: 0;
      top: 0;
    }
  }

  .description {
    margin-top: 0.5em;
  }
}
</style>
