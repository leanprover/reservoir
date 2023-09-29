<script setup lang="ts">
import manifest from '~/manifest.json'
import SearchIcon from '~icons/mdi/magnify'
import AutoComplete from 'primevue/autocomplete'
import { AutoCompleteCompleteEvent, AutoCompleteChangeEvent } from 'primevue/autocomplete'

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

const allPkgs = manifest.matrix
type Package = typeof allPkgs[number]

const query = ref()
const selectedPkg = ref<Package>()
const filteredPkgs = ref(allPkgs)
const filter = (event: AutoCompleteCompleteEvent) => {
  const results = allPkgs.filter((pkg) => pkg.name.indexOf(event.query) > -1)
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
    navigateTo(`/packages/${encodeURIComponent(pkg.id)}`)
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
      placeholder="Press 'S' to focus this searchbox..." optionLabel="name"
      v-model="query" :suggestions="filteredPkgs" :autoOptionFocus="false"
      @complete="filter" @change="onChange" @keyup.enter="commit"
      :virtualScrollerOptions="{ itemSize: 50 }">
      <template #option="slotProps">
        <div @click="commit($event, slotProps.option)">
          <h4>{{ slotProps.option.name }}</h4>
          <div class="description">{{ slotProps.option.description }}</div>
        </div>
      </template>
    </AutoComplete>
    <div tabindex="0" class="search-button" @click="commit" @keyup.enter="commit">
      <SearchIcon width="100%" height="100%" class="icon"/>
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
        color: var(--light-text-color);
        background-color: var(--light-accent-color);
      }

      &[data-p-focus="true"] {
        color: var(--light-text-color);
        background-color: var(--dark-accent-color);
      }

      .description {
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
