<script setup lang="ts">
import { Tippy } from 'vue-tippy'
import ForwardIcon from '~icons/mdi/chevron-right'
import type { RouteLocationRaw } from 'vue-router'
const props = defineProps<{title: string, list: Package[], to: RouteLocationRaw}>()
const findBuild = (pkg: Package) => (
  pkg.builds.find(b => b.built) ??
  pkg.builds.find(b => b.toolchain === latestToolchain.name) ??
  pkg.builds[0]
)
</script>

<template>
  <div class="highlight-category">
    <h3 class="title">{{ props.title }}</h3>
    <ol class="short-list">
      <li class="card" v-for="pkg in props.list" :key="pkg.fullName">
        <BuildOutcome class="prefix icon" :build="findBuild(pkg)" :mark-outdated="true"/>
        <Tippy class="text" :on-show="() => { if (!pkg.description) return false }">
          <NuxtLink class="soft-link" :to="pkgLink(pkg)">
            <div class="name">{{ pkg.name }}</div>
            <ForwardIcon class="suffix icon"/>
          </NuxtLink>
          <template #content>
            <div class="tooltip">{{ pkg.description }}</div>
          </template>
        </Tippy>
      </li>
    </ol>
    <div class="see-more">
      <NuxtLink class="hard-link" :to="props.to">
        <span>All {{ props.title.toLocaleLowerCase() }}</span>
        <ForwardIcon class="suffix icon"/>
      </NuxtLink>
    </div>
  </div>
</template>

<style scoped lang="scss">
.title {
  margin-bottom: 1em;
}

.short-list {
  list-style: none;

  li {
    display: flex;
    flex-direction: row;
    align-items: center;

    margin: 0 0 0.8em 0;
    padding: 2em;

    .text {
      display: flex;
      align-items: center;
      flex-grow: 1;
      min-width: 0;
    }

    .build-outcome {
      font-size: 1.2em;
    }

    a {
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-grow: 1;
      min-width: 0;

      .name {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        flex-grow: 1;
      }
    }
  }
}

.see-more {
  display: flex;
  justify-content: center;
  margin-top: 1em;

  a {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}
</style>
