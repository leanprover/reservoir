<script setup lang="ts">
import manifest from '~/manifest.json'
import StarIcon from '~icons/ion/star'
import Paginator from 'primevue/paginator'
import Dropdown from 'primevue/dropdown'

const toArray = <T,>(a: T | T[]) => Array.isArray(a) ? a: [a]

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
const query = computed(() => toArray(route.query.q).at(-1))
const querySortKey = toArray(route.query.sort).filter(isSortKey).at(-1)
const sortKey = ref<SortKey>(querySortKey ?? "stars")
const sort = (matrix: typeof manifest.matrix, key: SortKey | "") => {
  switch (key) {
    case "stars":
      return matrix.sort((a, b) => b[key] - a[key])
    case "createdAt":
      return matrix.sort((a, b) => new Date(b[key]).getTime() - new Date(a[key]).getTime())
    case "updatedAt":
      return matrix.sort((a, b) => new Date(b[key]).getTime() - new Date(a[key]).getTime())
    case "fullName":
      return matrix.sort((a, b) => a[key].localeCompare(b[key]))
    default:
      return matrix
  }
}
const fullMatrix = computed(() => {
  const q = query.value
  let matrix = [...manifest.matrix]
  if (q) {
    matrix = matrix.filter((e) => e.name.indexOf(q) > -1)
  }
  return sort(matrix, sortKey.value)
})
const numResults = computed(() => fullMatrix.value.length)

const numRows = 20
const first = ref(parseInt(toArray(route.query.page).at(-1)!) || 0)
const last = computed(() => Math.min(first.value + numRows, fullMatrix.value.length))
const matrix = computed(() => {
  const i = first.value
  return fullMatrix.value.slice(i, i+numRows)
});
</script>

<template>
  <div class="search-page">
    <div class="page-header">
      <h2 v-if="query">Search Results <span class="query">for '{{ query }}'</span></h2>
      <h2 v-else>All Packages</h2>
    </div>
    <div class="no-results" v-if="matrix.length === 0">
      <h3>
        <span>0 packages found. </span>
        <a href="https://lean-lang.org/lean4/doc/quickstart.html">Get started</a>
        <span> to create your own!</span>
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
          <Dropdown class="dropdown" panelClass="sort-panel" :autoOptionFocus="false"
            v-model="sortKey" :options="(sortOptions as any)" optionLabel="name" optionValue="value">
            <template #option="slotProps">
              <NuxtLink :to="{path: '/packages', query: {q: query, sort: slotProps.option.value}}">
                {{ slotProps.option.name }}
              </NuxtLink>
            </template>
          </Dropdown>
        </div>
      </div>
      <ol class="results-list">
        <li class="card" v-for="pkg in matrix" :key="pkg.id">
          <NuxtLink class="name" :to="`/packages/${encodeURIComponent(pkg.id)}`">
            <h3>{{pkg.fullName}}</h3>
          </NuxtLink>
          <p>
            <span v-if="pkg.description">{{ pkg.description }}</span>
            <em v-else>No description provided.</em>
          </p>
          <ul class="links">
            <li v-if="pkg.homepage"><a :href="pkg.homepage">Homepage</a></li>
            <li><a :href="pkg.url">Repository</a></li>
            <li class="stars"><StarIcon class="icon"/>{{ pkg.stars }}</li>
            <li><BuildOutcome :outcome="pkg.outcome"/></li>
          </ul>
        </li>
      </ol>
      <Paginator :pt="{root: 'paginator'}"
        v-model:first="first" :rows="numRows" :total-records="numResults"/>
    </div>
  </div>
</template>

<style lang="scss">
.search-page {
  max-width: 100vw;

  .page-header {
    padding: 1em;
    background-color: var(--medium-color);
    border-radius: 6px;
    margin-bottom: 1em;

    .query {
      color: var(--dark-color);
    }
  }

  .no-results {
    margin-top: 2em;

    a {
      color: var(--dark-accent-color);

      &:hover {
        color: var(--light-accent-color);
      }
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
            margin-right: 0.8em;

            a {
              color: var(--dark-accent-color);

              &:hover, &:focus {
                color: var(--light-accent-color);
              }

              &:focus {
                outline: none;
              }
            }

            &.stars {
              display: flex;
              align-items: center;
              .icon {
                width: 1em;
                height: 1em;
                color: var(--star-color);
                margin-right: 0.5em;
              }
            }

            .build-outcome {
              width: 1em;
              height: 1em;
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
