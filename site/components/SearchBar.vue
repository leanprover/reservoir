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

type PackageResult = Package &
  {highlightedName: VNode, highlightedDescription: VNode | null}

const highlightSpan = (text: string, start: number, end: number): VNode => {
  return h('span', [
    text.slice(0, start),
    h('span', {class: 'highlight'}, text.slice(start, end)),
    text.slice(end),
  ])
}

const query = ref()
const selectedPkg = ref<Package>()
const filteredPkgs = ref<Package[]>(packages)
const filter = (event: AutoCompleteCompleteEvent) => {
  const q = event.query.toLowerCase()
  const results = packages.reduce<PackageResult[]>((pkgs, pkg) => {
    const idx = pkg.name.toLowerCase().indexOf(q)
    if (idx > -1) {
      const result = Object.assign(pkg, {
        highlightedName: highlightSpan(pkg.name, idx, idx+q.length),
        highlightedDescription: pkg.description ? h('span', pkg.description) : null
      })
      pkgs.push(result)
      return pkgs
    }
    const fullIdx = pkg.fullName.toLowerCase().indexOf(q)
    if (fullIdx > -1) {
      const result = Object.assign(pkg, {
        highlightedName: highlightSpan(pkg.fullName, fullIdx, fullIdx+q.length),
        highlightedDescription:  pkg.description ? h('span', pkg.description) : null
      })
      pkgs.push(result)
      return pkgs
    }
    if (pkg.description) {
    const descrIdx = pkg.description.toLowerCase().indexOf(q)
      if (descrIdx && descrIdx > -1) {
        const result = Object.assign(pkg, {
          highlightedName: h('span', pkg.name),
          highlightedDescription: highlightSpan(pkg.description, descrIdx, descrIdx+q.length)
        })
        pkgs.push(result)
        return pkgs
      }
    }
    return pkgs
  }, [])
  filteredPkgs.value = results
}
const onChange = (event: AutoCompleteChangeEvent) => {
  if (typeof event.value == "string") {
    query.value = event.value
    selectedPkg.value = undefined
  } else {
    query.value = event.value.fullName
    selectedPkg.value = event.value
  }
}
const commit = (event: Event, clickedPkg?: Package) => {
  event.preventDefault()
  const pkg = clickedPkg ?? selectedPkg.value
  if (pkg) {
    query.value = ""
    selectedPkg.value = undefined
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
          <h4 class="name">
            <component :is="slotProps.option.highlightedName"/>
          </h4>
          <div class="description">
            <span v-if="slotProps.option.highlightedDescription">
              <component :is="slotProps.option.highlightedDescription"/>
            </span>
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
    height: 1.3em;
    width: 2em;

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
        background-color: var(--dark-accent-color);

        .name .highlight, .description .highlight {
          color: inherit;
        }
      }

      .name .highlight, .description .highlight {
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
