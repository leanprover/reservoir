<script setup lang="ts">
const route = useRoute()
const keywords = computed(() => toArray(route.query.keyword).filter((x): x is string => !!x))
const query = computed(() => toArray(route.query.q).at(-1) || '')
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
  return pkgs
})

const sortOptions: NonEmptyArray<SortOption<Package>> = [
  {label: "Stars", key: "stars", sort: (a, b) => b.stars - a.stars},
  {label: "Date Created", key: "createdAt", sort: (a, b) => b.createdAt.localeCompare(a.createdAt)},
  {label: "Date Updated", key: "updatedAt", sort: (a, b) => b.updatedAt.localeCompare(a.updatedAt)},
  {label: "Package Name", key: "name", sort: (a, b) => {
    return a.name.localeCompare(b.name) || b.stars - a.stars
  }},
  {label: "Package Owner", key: "owner", sort: (a, b) => {
    return a.owner.localeCompare(b.owner) || a.name.localeCompare(b.name)
  }},
]
</script>

<template>
  <div class="search-page">
    <div class="page-header">
      <SearchBar class="packages-search-bar" />
      <h3 v-if="query || keywords.length > 0">
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
      </h3>
      <h2 v-else>All Packages</h2>
    </div>
    <div class="no-results" v-if="results.length === 0">
      <h3>
        <p>
          <span>0 packages found. </span>
          <span>
            <a class="hard-link" href="https://calm-wisp-fefd29.netlify.app/lean4/doc/quickstart.html">Get started</a>
            to create your own!
          </span>
        </p>
        <p>
          Your package not here? Verify that your package meets the
          <NuxtLink class="hard-link" to="inclusion-criteria">Reservoir inclusion criteria</NuxtLink>.
        </p>
      </h3>
    </div>
    <SortedList v-else class="results" :sortOptions="sortOptions"
      :items="results" :itemKey="item => item.fullName">
      <template #total-label>
        total results
      </template>
      <template #item="{item}">
        <PackageResult :pkg="item"/>
      </template>
    </SortedList>
  </div>
</template>

<style lang="scss">

.packages-search-bar {
  margin-bottom: 2em;
  width: 100%;
}

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

  .pkg-result {
    padding: 2em;

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
</style>
