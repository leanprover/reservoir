<script setup lang="ts">
import manifest from '~/manifest.json'
import StarIcon from '~icons/ion/star'

const sortKeys = ["fullName", "stars", "createdAt", "updatedAt"] as const
type SortKey = typeof sortKeys[number]
const isSortKey = (x: any): x is SortKey => sortKeys.includes(x)

const route = useRoute()
const querySortKey = Array(route.query.sort).filter(isSortKey).at(-1)
const sortKey = ref<SortKey | "">(querySortKey || "stars")
const matrix = computed(() => {
  const key = sortKey.value
  const matrix = [...manifest.matrix]
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
});
const numResults = manifest.matrix.length
</script>

<template>
  <div class="search-page">
    <div class="page-header">
      <h2>All Packages</h2>
    </div>
    <div class="results">
      <div class="results-header">
        <div>Displaying <strong>{{ numResults }}</strong> results</div>
        <div class="sort-by">
          <span class="label">Sort by</span>
          <select class="dropdown" v-model="sortKey">
            <option value="" disabled selected>Select one...</option>
            <option value="stars">Stars</option>
            <option value="createdAt">Date Created</option>
            <option value="updatedAt">Date Updated</option>
            <option value="fullName">Alphabetical</option>
          </select>
        </div>
      </div>
      <ol class="results-list">
        <li class="card" v-for="pkg in matrix" :key="pkg.id">
          <h3><NuxtLink :to="`/packages/${pkg.id}`">{{pkg.fullName}}</NuxtLink></h3>
          <p>{{pkg.description}}</p>
          <ul class="links">
            <li v-if="pkg.homepage"><a :href="pkg.homepage">Homepage</a></li>
            <li><a :href="pkg.url">Repository</a></li>
            <li class="stars"><StarIcon class="icon"/>{{ pkg.stars }}</li>
            <li><BuildOutcome :outcome="pkg.outcome"/></li>
          </ul>
        </li>
      </ol>
    </div>
  </div>
</template>

<style lang="scss">
.search-page {
  .page-header {
    padding: 1em;
    background-color: var(--medium-color);
    border-radius: 6px;
    margin-bottom: 1em;
  }

  .results {
    .results-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .sort-by {
        display: flex;
        align-items: center;

        .label {
          margin-right: 0.5em;
        }

        .dropdown {
          padding: 0.5em 0.8em;
          background-color: var(--medium-color);
          border-radius: 6px;

          option:hover {
            background-color: var(--dark-color);
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

        h3 {
          margin-bottom: 0.8em;

          a:hover {
            color: var(--light-accent-color);
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

              &:hover {
                color: var(--light-accent-color);
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
  }
}
</style>
