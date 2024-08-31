<script setup lang="ts">
import Paginator from 'primevue/paginator'
import Dropdown from 'primevue/dropdown'

const toArray = <T>(a: T | T[]) => Array.isArray(a) ? a : [a]

const sortOptions = [
  {name: "Stars", value: "stars"},
  {name: "Date Created", value: "createdAt"},
  {name: "Date Updated", value: "updatedAt"},
  {name: "Alphabetical", value: "fullName"},
] as const
type SortKey = typeof sortOptions[number]['value']
const sortKeys: SortKey[] = sortOptions.map(opt => opt.value)
const isSortKey = (x: any): x is SortKey => sortKeys.includes(x)

const route = useRoute()
const keywords = computed(() => toArray(route.query.keyword).filter((x): x is string => !!x))
const query = computed(() => toArray(route.query.q).at(-1) || '')
const querySortKey = toArray(route.query.sort).filter(isSortKey).at(-1)
const sortKey = ref<SortKey>(querySortKey ?? "stars")
const sort = (pkgs: Package[], key: SortKey | "") => {
  switch (key) {
    case "stars":
      return pkgs.sort((a, b) => b[key] - a[key])
    case "createdAt":
      return pkgs.sort((a, b) => new Date(b[key]).getTime() - new Date(a[key]).getTime())
    case "updatedAt":
      return pkgs.sort((a, b) => new Date(b[key]).getTime() - new Date(a[key]).getTime())
    case "fullName":
      return pkgs.sort((a, b) => a[key].localeCompare(b[key]))
    default:
      return pkgs
  }
}
const results = computed(() => {
  let pkgs = [...packages]
  const q = query.value.toLocaleLowerCase()
  const kws = keywords.value
  if (q || kws.length > 0) {
    pkgs = pkgs.filter(e => {
      if (q && e.name.toLocaleLowerCase().indexOf(q) == -1) return false
      if (kws.some(k => !e.keywords.includes(k))) return false
      return true
    })
  }
  return sort(pkgs, sortKey.value)
})
const numResults = computed(() => results.value.length)

const numRows = 20
const first = ref(parseInt(toArray(route.query.first).at(-1)!) || 0)
const last = computed(() => Math.min(first.value + numRows, results.value.length))
const resultPage = computed(() => {
  const i = first.value
  return results.value.slice(i, i+numRows)
});
</script>

<template>
  <div class="search-page">
    <div class="page-header">
      <h2 v-if="query || keywords.length > 0">
        Search Results
        <span class="search">
          for
          <span class="query" v-if="query">'{{ query }}'</span>
          <span v-if="query && keywords.length > 0"> and </span>
          <span class="keywords" v-if="keywords.length > 0">
           {{ keywords.length > 1 ? 'keywords' : 'keyword' }}
           {{ keywords.map(k => `'${k}'`).join(' & ') }}
          </span>
        </span>
      </h2>
      <h2 v-else>All Packages</h2>
    </div>
    <div class="no-results" v-if="numResults === 0">
      <h3>
        <p>
          <span>0 packages found. </span>
          <span>
            <a class="hard-link" href="https://lean-lang.org/lean4/doc/quickstart.html">Get started</a>
            to create your own!
          </span>
        </p>
        <p>
          Your package not here? Verify that your package meets the
          <NuxtLink class="hard-link" to="inclusion-criteria">Reservoir inclusion criteria</NuxtLink>.
        </p>
      </h3>
    </div>
    <div v-else class="results">
      <div class="results-header">
        <div class="info">
          <span class="displaying">Displaying </span>
          <strong>{{ first+1 }}-{{ last }}</strong>
          <span> of </span>
          <strong>{{ numResults }}</strong>
          <span class="total-descr"> total results</span>
        </div>
        <div class="sort-by">
          <span class="label">Sort by</span>
          <Dropdown class="dropdown" panelClass="sort-panel" :autoOptionFocus="false" @change="first = 0"
            v-model="sortKey" :options="(sortOptions as any)" optionLabel="name" optionValue="value">
            <template #option="slotProps">
              <NuxtLink :to="{path: '/packages', query: {q: query, keyword: keywords, sort: slotProps.option.value}}">
                {{ slotProps.option.name }}
              </NuxtLink>
            </template>
          </Dropdown>
        </div>
      </div>
      <ol class="results-list">
        <PackageResult v-for="pkg in resultPage" :key="pkg.fullName" :pkg="pkg"/>
      </ol>
      <Paginator :pt="{root: 'paginator'}"
        v-model:first="first" :rows="numRows" :total-records="numResults"/>
    </div>
  </div>
</template>

<style lang="scss">
.search-page {
  max-width: 100vw;

  .page-header .search {
    color: var(--dark-color);
    font-size: 0.9em;
  }

  .no-results {
    margin-top: 2em;

    p {
      margin-bottom: 1em;
    }
  }

  .results {
    .results-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .info {
        @media only screen and (max-width: 500px) {
          .total-descr { display: none; }
        }

        @media only screen and (max-width: 600px) {
          .displaying { display: none; }
        }
      }

      .sort-by {
        display: flex;
        align-items: center;

        .label {
          margin-right: 0.5em;
        }

        .dropdown {
          display: flex;
          align-items: center;
          justify-content: space-between;

          padding: 0.5em 0.8em;
          background-color: var(--medium-color);
          border-radius: 6px;
          width: 10em;

          &:has(*:focus) {
            color: var(--light-text-color);
            background-color: var(--dark-color);
          }

          *:focus {
            outline: none;
          }
        }
      }
    }

    ol.results-list {
      list-style: none;
      margin: 1em 0;

      & > li {
        padding: 1em;
        margin-bottom: 1em;

        .name {
          display: block;
          margin-bottom: 0.8em;

          h3 {
            overflow: hidden;
            text-overflow: ellipsis;
            text-wrap: nowrap;
            display: block;
            width: 100%;
          }

          &:hover, &:focus   {
            color: var(--light-accent-color);
          }

          &:focus {
            outline: none;
          }
        }

        ul.links {
          list-style: none;

          display: flex;
          flex-direction: row;
          align-items: center;
          margin-top: 1em;

          & > li {
            display: flex;
            margin-right: 0.8em;

            &.stars {
              display: flex;
              align-items: center;
              line-height: 1em;

              .icon {
                color: var(--star-color);
              }
            }
          }
        }
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
    }
  }
}

.sort-panel {
  background-color: var(--card-color);

  border: 1px solid var(--medium-color);
  background-color: var(--card-bg-color);
  border-radius: 6px;

  option:hover {
    background-color: var(--dark-color);
  }

  ul {
    list-style-type: none;

    li {
      a {
        width: 100%;
        height: 100%;
        display: block;
        padding: 0.3em 0.8em;
      }

      &:hover {
        background-color: var(--medium-color);
      }

      &[data-p-focused="true"] {
        color: var(--light-accent-color);
      }
    }
  }
}
</style>
