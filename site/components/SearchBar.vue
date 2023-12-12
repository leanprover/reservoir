<script setup lang="ts">
import SearchIcon from '~icons/mdi/magnify'
import AutoComplete from 'primevue/autocomplete'
import type { AutoCompleteCompleteEvent, AutoCompleteChangeEvent } from 'primevue/autocomplete'

const ctrl = ref()
const keyHandler = (e: KeyboardEvent) => {
  if (e.key === "S" || e.key === "s") {
    if (ctrl.value) ctrl.value.$refs.focusInput.focus()
  }
}
onMounted(() => {
  window.addEventListener('keyup', keyHandler)
})
onUnmounted(() => {
  window.removeEventListener('keyup', keyHandler)
})

type PackageResult = Package & {highlightedName : VNode}

const query = ref()
const selectedPkg = ref<Package>()
const filteredPkgs = ref<Package[]>(packages)
const filter = (event: AutoCompleteCompleteEvent) => {
  const q = event.query.toLocaleLowerCase()
  const results = packages.reduce<PackageResult[]>((pkgs, pkg) => {
    const idx = pkg.name.toLocaleLowerCase().indexOf(q)
    if (idx > -1) {
      const result = Object.assign(pkg, {
        highlightedName: h('span', [
          pkg.name.slice(0, idx),
          h('span', {class: 'highlight'}, pkg.name.slice(idx, idx+q.length)),
          pkg.name.slice(idx+q.length),
        ])
      })
      pkgs.push(result)
    }
    return pkgs
  }, [])
  if (results.length === 0) ctrl.value.hide()
  filteredPkgs.value = results;
}
const onChange = (event: AutoCompleteChangeEvent) => {
  if (typeof event.value == "string") {
    query.value = event.value
    selectedPkg.value = undefined
  } else {
    query.value = event.value.name
    selectedPkg.value = event.value
  }
}
const commit = (event: Event, clickedPkg?: Package) => {
  event.preventDefault()
  const pkg = clickedPkg ?? selectedPkg.value
  if (pkg) {
    query.value = ""
    selectedPkg.value = undefined
    console.log(pkg)
    navigateTo(pkgLink(pkg))
  } else {
    const q = query.value
    if (q) {
      ctrl.value.hide()
      navigateTo({path: '/packages', query: {'q': q}})
    } else {
      navigateTo('/packages')
    }
  }
}
</script>

<template>
  <div class="search-bar">
    <AutoComplete ref="ctrl"
      class="search-control" panelClass="search-panel"
      placeholder="Press 'S' to start searching..." optionLabel="name"
      v-model="query" :suggestions="filteredPkgs" :autoOptionFocus="false"
      @complete="filter" @change="onChange" @keyup.enter="commit"
      :virtualScrollerOptions="{ itemSize: 50 }">
      <template #option="slotProps">
        <div @click="commit($event, slotProps.option)">
          <h4 class="name"><component :is="slotProps.option.highlightedName"/></h4>
          <div class="description">
            <span v-if="slotProps.option.description">{{ slotProps.option.description }}</span>
            <em v-else>No description provided.</em>
          </div>
        </div>
      </template>
    </AutoComplete>
    <div tabindex="0" class="search-button" @click="commit" @keyup.enter="commit">
      <SearchIcon width="100%" height="100%"/>
    </div>
  </div>
</template>

<style lang="scss">
.search-bar {
  display: flex;
  align-items: center;
  font-size: 1.3em;
  border-radius: 6px;
  outline: none;

  &:has(input:focus, .search-button:focus) {
    box-shadow: 0 0 0 0.3rem var(--dark-accent-color);
  }

  background-color: var(--dark-accent-color);

  &:has(.search-button:hover, .search-button:focus) {
    background-color: var(--light-accent-color);
  }

  .search-control {
    flex-grow: 1;

    input {
      padding: 0.3rem;
      border-radius: 6px 0 0 6px;
      border: none;
      width: 100%;

      &:focus {
        outline: none;
      }
    }
  }

  .search-button {
    cursor: pointer;
    padding: 0 0.3em;
    height: 1.3em;
    flex: 0 0 auto;

    &:focus {
      outline: none
    }
  }
}

.search-panel {
  background-color: var(--card-bg-color);
  border: 1px solid black;
  border-radius: 6px;
  height: 40vh;

  .p-virtualscroller {
    height: 100% !important;
  }

  ul {
    width: 100%;
    list-style: none;

    li {
      display: flex;
      flex-direction: column;
      justify-content: center;
      padding: 0.3rem;
      cursor: pointer;

      &:not(:first-child) {
        border-top: 1px solid black;
      }

      &:hover {
        background-color: var(--medium-color);
      }

      &[data-p-focus="true"] {
        color: var(--light-text-color);
        // background-color: var(--dark-color);
        background-color: var(--dark-accent-color);

        .name .highlight {
          color: inherit;
        }
      }

      .name .highlight {
        color: var(--dark-accent-color);
      }

      .name, .description {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
  }
}

.p-hidden-accessible {
  display: none
}
</style>
