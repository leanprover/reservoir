<script setup lang="ts" generic="T">
import Dropdown from 'primevue/dropdown'
import Paginator from 'primevue/paginator'

const props = defineProps<{
  items: T[],
  itemKey: (item: T) => number | string | symbol
  sortOptions: NonEmptyArray<SortOption<T>>
}>()

const route = useRoute()
const sortKeys = new Set(props.sortOptions.map(opt => opt.key))
const querySortKey = toArray(route.query.sort).filter(x => x && sortKeys.has(x)).at(-1)
const querySortFn = props.sortOptions.find(opt => opt.key == querySortKey)?.sort
const sortFn = ref(querySortFn ?? props.sortOptions[0].sort)
const items = computed(() => Array(...props.items).sort(sortFn.value))

const numRows = ref(20)
const numItems = computed(() => items.value.length)
const first = ref(parseInt(toArray(route.query.first).at(-1)!) || 0)
const last = computed(() => Math.min(first.value + numRows.value, items.value.length))
const itemPage = computed(() => {
  const i = first.value
  return items.value.slice(i, i+numRows.value)
});

const sortLink = function(key: string) {
  const newQuery = Object.assign({}, route.query, {sort: key})
  delete newQuery.first
  return {path: route.path, query: newQuery}
}
</script>

<template>
  <div class="sorted-list">
    <div class="list-header">
      <slot name="header" :first="first" :last="last" :total="numItems">
        <div class="list-info">
          <span class="displaying">Displaying </span>
          <strong>{{ last > 0 ? first+1 : 0 }}-{{ last }}</strong>
          <span> of </span>
          <strong>{{ numItems }}</strong>
          <span class="total-label"><slot name="total-label"/></span>
        </div>
      </slot>
      <div class="sort-by">
        <span class="label nowrap">Sort by</span>
        <Dropdown class="dropdown" panelClass="dropdown-panel" :autoOptionFocus="false" @change="first = 0"
          v-model="sortFn" :options="sortOptions" optionLabel="label" optionValue="sort">
          <template #option="{option}">
            <NuxtLink class="dropdown-item" :to="sortLink(option.key)">{{option.label}}</NuxtLink>
          </template>
        </Dropdown>
      </div>
    </div>
    <ol class="item-list">
      <template v-for="item in itemPage" :key="itemKey(item)">
        <slot name="item" :item="item"/>
      </template>
    </ol>
    <Paginator
      v-model:first="first" :totalRecords="numItems"
      v-model:rows="numRows" :rowsPerPageOptions="[10, 20, 50, 100, 250, 500]"
      :pt="{root: 'paginator', rowPerPageDropdown: {root: 'dropdown', panel: 'dropdown-panel', itemLabel: 'dropdown-item'}}"/>
  </div>
</template>

<style lang="scss">
.sorted-list {
  & > .list-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .list-info {
      @media only screen and (max-width: 30em) {
        .total-label { display: none; }
      }

      @media only screen and (max-width: 35em) {
        .displaying { display: none; }
      }
    }

    .sort-by {
      display: flex;
      align-items: center;
      margin-left: 0.5em;

      .label {
        margin-right: 0.5em;
      }

      .dropdown {
        width: 10em;
      }
    }
  }

  & > ol {
    list-style: none;
    margin: 1em 0;

    & > li {
      margin-bottom: 1em;
    }
  }

  .paginator {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 1em 0;

    button {
      border-radius: 6px;
      color: var(--dark-text-color);
      padding: 0.3em 0.5em;
      margin: 0em 0.2em;

      &:hover {
        cursor: pointer;
        background-color: var(--medium-color);
      }

      &:focus {
        outline: none;
        color: var(--light-accent-color);
      }

      &[data-p-highlight="true"] {
        color: var(--light-text-color);
        background-color: var(--dark-color);
      }
    }

    .dropdown {
      width: 5em;
    }
  }
}

.dropdown {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;

  padding: 0.5em 0.8em;
  background-color: var(--medium-color);
  border-radius: 6px;

  &:has(*:focus) {
    color: var(--light-text-color);
    background-color: var(--dark-color);
  }

  *:focus {
    outline: none;
  }
}

.dropdown-panel {
  background-color: var(--card-color);

  border: 1px solid var(--medium-color);
  background-color: var(--card-bg-color);
  border-radius: 6px;

  ul {
    list-style-type: none;

    li {
      .dropdown-item {
        width: 100%;
        height: 100%;
        display: block;
        padding: 0.3em 0.8em;
        cursor: pointer
      }

      &:not([data-p-focused="true"]):hover {
        color: var(--dark-accent-color);
      }

      &[data-p-focused="true"] {
        background-color: var(--dark-color);
        color: var(--light-color);
      }
    }
  }
}
</style>
