<script setup lang="ts">
import GitIcon from '~icons/mdi/git'
import FolderIcon from '~icons/mdi/folder'
import UnknownIcon from '~icons/mdi/help'
import TagIcon from '~icons/mdi/tag'
import AtIcon from '~icons/mdi/at'
import ReservoirIcon from '~/public/favicon.svg?component'
import { Tippy } from 'vue-tippy'

const props = defineProps<{package: Package, dep: PackageDep, upstream: boolean}>()
const dep = computed(() => props.dep)
const depPkg = computed(() => dep.value.fullName ? getPkg(dep.value.fullName) : undefined)
const ver = computed(() => {
  const pkg = props.upstream ? depPkg.value : props.package
  return pkg?.versions.find(ver => ver.revision == dep.value.rev)
})
const depName = computed(() => {
  return props.upstream ? dep.value.name : (depPkg.value ? depPkg.value.fullName : dep.value.name)
})
const verId = computed(() => {
  if (dep.value.version != '0.0.0') return dep.value.version
  if (ver.value?.tag) return ver.value.tag
  if (dep.value.rev) return dep.value.rev.slice(0, 7)
  return '0.0.0'
})
</script>

<template>
  <li class="dep-item card">
    <div v-if="upstream" class="dep-type">
      <Tippy>
        <ReservoirIcon v-if="dep.scope && depPkg" class="icon"/>
        <GitIcon v-else-if="dep.type == 'git'" class="icon"/>
        <FolderIcon v-else-if="dep.type == 'path'" class="icon"/>
        <UnknownIcon v-else class="icon"/>
        <template #content>
          <div class="dep-tooltip">
            <span v-if="dep.scope">Registry dependency.</span>
            <span v-else-if="dep.type == 'git'">Git dependency.</span>
            <span v-else-if="dep.type == 'path'">Local path dependency.</span>
            <span v-else>(BUG) Unknown dependency..</span>
            <br/>
            <span v-if="depPkg">Found on Reservoir.</span>
            <span v-else>Not found on Reservoir.</span>
          </div>
        </template>
      </Tippy>
    </div>
    <div class="dep-info">
      <h3 class="dep-header">
        <NuxtLink class="dep-name dep-link" v-if="depPkg" :to="pkgLink(depPkg)">
          <span>{{depName}}</span>
        </NuxtLink>
        <span class="dep-name" v-else>{{depName}}</span>
        <span class="dep-version">
          <AtIcon v-if="upstream" class="dep-at icon"/>
          <span v-else class="dep-at">uses</span>
          <span class="version-id">
            <TagIcon v-if="dep.version == '0.0.0' && ver?.tag" class="icon"/>
            <code>{{verId}}</code>
          </span>
        </span>
      </h3>
      <div v-if="depPkg && depPkg.description" class="description">
        {{ depPkg.description  }}
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
  padding: 1em;
  z-index: 0;

  &:has(.dep-link):hover {
    background-color: var(--medium-color);
  }

  &:has(.dep-link:focus) {
    border-width: 2px;
    border-color: var(--dark-color);
  }

  .dep-type {
    margin-left: 0.5em;
    margin-right: 1.2em;
    position: relative;
    z-index: 1;

    .icon {
      width: 1.8em;
      height: 1.8em;
    }
  }

  .dep-info {
    min-width: 0;
  }

  .dep-header {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
  }

  .dep-name {
    display: inline-block;
    overflow: hidden;
    text-overflow: ellipsis;
    text-wrap: nowrap;
    margin-right: 0.4em;
  }

  .dep-version {
    display: inline-flex;
    align-items: center;
    font-size: 0.8em;
    color: var(--dark-color);

    .version-id {
      display: inline-flex;
      align-items: center;
      padding: 0.2em 0.3em;
      border-radius: 5px;
      background-color: var(--light-color);

      .icon {
        width: 1.2em;
        height: 1.2em;
        margin-right: 0.3em;
      }
    }

    .dep-at {
      margin-right: 0.5em;

      &.icon {
        width: 1.3em;
        height: 1.3em;
      }
    }
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

.dep-tooltip {
  text-align: center
}
</style>
