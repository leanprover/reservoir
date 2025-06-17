<script setup lang="ts">
const route = useRoute()
const owner = route.params.owner as string
const name = route.params.name as string
const maybePkg = findPkg(owner, name)

definePageMeta({
  layout: 'page',
})

if (maybePkg === undefined) {
  throw createError({
    statusCode: 404,
    statusMessage: `Package '${owner}/${name}' not found`,
    fatal: true
  })
}
const pkg: Package = maybePkg
if (pkg.owner !== owner || pkg.name !== name) {
  navigateTo(pkgLink(pkg), { replace: true })
}

useHead({
  title: pkg.name,
  meta: pkg.description ? [{ name: 'description', content: pkg.description }] : undefined
})

defineOgImageComponent('Generic', {
  title: pkg.name,
  description: pkg.description,
  hasNoDescription: !pkg.description
})

const navTab = computed(() => {
  return route.path == pkgLink(pkg) ? 'readme' : route.path.split('/').at(-1)
})

const pkgVer = computed(() => {
  const rev = toArray(route.query.rev).at(-1)
  if (rev) {
    const res = pkg.versions.find(ver => ver.revision == rev)
    if (res) return res
  }
  const tag = toArray(route.query.tag).at(-1)
  if (tag) {
    const res = pkg.versions.find(ver => ver.tag == tag)
    if (res) return res
  }
  const verId = toArray(route.query.ver).at(-1)
  if (verId) {
    const res = pkg.versions.find(ver => ver.version == verId)
    if (res) return res
  }
  return pkg.versions.at(0)
})

function tabLink(tab?: string) {
  const newQuery: any = {}
  for (const key in ['rev', 'tag', 'ver']) {
    newQuery[key] = route.query[key]
  }
  const path = pkgLink(pkg)
  return { path: tab ? `${path}/${tab}` : path, query: route.query }
}
</script>

<template>
  <nav class="page-nav">
    <ul class="container">
      <li :class="{ 'active': navTab == 'readme' }">
        <NuxtLink :to="tabLink()">Readme</NuxtLink>
      </li>
      <li v-if="pkg.versions.length > 0 || navTab == 'versions'" :class="{ 'active': navTab == 'versions' }">
        <NuxtLink :to="tabLink('versions')">Versions ({{ pkg.versions.length }})</NuxtLink>
      </li>
      <li v-if="pkgVer && pkgVer.dependencies.length > 0 || navTab == 'dependencies'"
        :class="{ 'active': navTab == 'dependencies' }">
        <NuxtLink :to="tabLink('dependencies')">Dependencies ({{ pkgVer?.dependencies?.length ?? 0 }})</NuxtLink>
      </li>
      <li v-if="pkg.dependents.length > 0 || navTab == 'dependents'" :class="{ 'active': navTab == 'dependents' }">
        <NuxtLink :to="tabLink('dependents')">Dependents ({{ pkg.dependents.length }})</NuxtLink>
      </li>
    </ul>
  </nav>

  <div class="contents">
    <div class="package-page">
      <div class="page-header">
        <div class="page-side">
          <h2>
            <img :src="`https://github.com/${pkg.owner}.png`" :alt="pkg.owner" width="40" height="40"/>
            <span>{{ pkg.name }}</span>
            <span class='version' v-if="pkgVer && pkgVer.version != '0.0.0'">v{{ pkgVer.version }}</span>
          </h2>
          <div class="description" v-if="pkg.description">{{ pkg.description }}</div>
          <div class="keywords" v-if="pkg.keywords.length > 0">
            <NuxtLink class="keyword hard-link" v-for="keyword in pkg.keywords"
              :to="{ path: '/packages', query: { keyword } }">
              #{{ keyword }}
            </NuxtLink>
          </div>
        </div>
        <div>

        </div>
      </div>
      <NuxtPage :package="pkg" :version="pkgVer" class="page-tab"></NuxtPage>
    </div>
  </div>
</template>

<style lang="scss">

.page-nav {
  width: 100%;
  border-bottom: 1px solid var(--color-border);

  ul {
    display: flex;
    list-style: none;
    border: 0px;

    li {
      border-width: 2px;
      padding: 1.2em 0.8em;
      font-size: 0.9rem;

      &.active {
        color: var(--dark-accent-color);
        background-color: var(--medium-color);
        border-color: var(--dark-color);
      }

      &:hover,
      &:focus {
        color: var(--dark-accent-color);
        border-color: var(--dark-color);
      }
    }

    @media only screen and (min-width: 600px) {
      flex-direction: row;
      border-bottom-style: solid;

      li {

        &.active,
        &:hover,
        &:focus {
          border-bottom-style: solid;
        }
      }
    }

    @media only screen and (max-width: 600px) {
      flex-direction: column;
      border-left-style: solid;

      li {
        padding: 1em;

        &.active,
        &:hover,
        &:focus {
          border-left-style: solid;
        }
      }
    }
  }
}

.package-page {
  margin-bottom: 1.5em;

  aside {
    margin-bottom: 1.5em;
  }

  .page-header {
    display: flex;
    justify-content: space-between;
  }

  .page-side {
    border-radius: 6px;
    margin-bottom: 1em;
    display: flex;
    flex-direction: column;
    gap: 10px;

    h2 {
      overflow: hidden;
      text-overflow: ellipsis;
      text-wrap: nowrap;
      gap: 10px;
      display: flex;
      align-items: center;

      img {
        border-radius: 7px;
      }
    }

    .version {
      margin-left: 0.5em;
      color: var(--dark-color);
      font-size: 0.9em;
    }

    .description {
      margin-top: 0.5em;
    }

    .keywords {
      margin-top: 0.75em;
      display: flex;
      flex-direction: row;
      flex-wrap: wrap;

      .keyword {
        white-space: nowrap;

        &:not(:last-child) {
          margin-right: 1rem;
        }
      }
    }
  }

  .page-tab {
    min-height: 45vh;
    gap: 30px;
  }
}
</style>
