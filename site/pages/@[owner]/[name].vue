<script setup lang="ts">
const route = useRoute()
const owner = route.params.owner as string
const name = route.params.name as string
const maybePkg = findPkg(owner, name)
if (maybePkg === undefined) {
  throw createError({
    statusCode: 404,
    statusMessage: `Package '${owner}/${name}' not found`,
    fatal: true
  })
}
const pkg: Package = maybePkg
if (pkg.owner !== owner || pkg.name !== name) {
  navigateTo(pkgLink(pkg), {replace: true})
}

useHead({
  title: pkg.name,
  meta: pkg.description ? [{name: 'description', content: pkg.description}] : undefined
})

defineOgImageComponent('Generic', {
  title: pkg.name,
  description: pkg.description,
  hasNoDescription: !pkg.description
})

const navTab = computed(() => {
  return route.path == pkgLink(pkg) ? 'readme' : route.path.split('/').at(-1)
})

const pkgVer = computed(() => pkg.versions.at(0))
</script>

<template>
  <div class="package-page">
    <div class="page-header">
      <h2>
        <span>{{ pkg.name }}</span>
        <span class='version' v-if="pkgVer && pkgVer.version != '0.0.0'">v{{pkgVer.version}}</span>
      </h2>
      <div class="description" v-if="pkg.description">{{ pkg.description }}</div>
      <div class="keywords" v-if="pkg.keywords.length > 0">
        <NuxtLink class="keyword hard-link" v-for="keyword in pkg.keywords" :to="{path: '/packages', query: {keyword}}">
          #{{ keyword }}
        </NuxtLink>
      </div>
    </div>
    <nav>
      <ul>
        <li :class="{'active': navTab == 'readme'}">
          <NuxtLink :to="{path: pkgLink(pkg)}">Readme</NuxtLink>
        </li>
        <li v-if="pkg.versions.length > 0 || navTab == 'versions'" :class="{'active': navTab == 'versions'}">
          <NuxtLink :to="{path: `${pkgLink(pkg)}/versions`}">Versions ({{pkg.versions.length}})</NuxtLink>
        </li>
        <li v-if="pkgVer && pkgVer.dependencies.length > 0 || navTab == 'dependencies'" :class="{'active': navTab == 'dependencies'}">
          <NuxtLink :to="{path: `${pkgLink(pkg)}/dependencies`}">Dependencies ({{pkgVer?.dependencies?.length ?? 0}})</NuxtLink>
        </li>
        <li v-if="pkg.dependents.length > 0 || navTab == 'dependents'" :class="{'active': navTab == 'dependents'}">
          <NuxtLink :to="{path: `${pkgLink(pkg)}/dependents`}">Dependents ({{pkg.dependents.length}})</NuxtLink>
        </li>
      </ul>
    </nav>
    <NuxtPage :package="pkg" class="page-tab"></NuxtPage>
  </div>
</template>

<style lang="scss">
.package-page {
  margin-bottom: 1.5em;

  .page-header {
    padding: 1.5em;
    background-color: var(--medium-color);
    border-radius: 6px;
    margin-bottom: 1em;

    h2 {
      overflow: hidden;
      text-overflow: ellipsis;
      text-wrap: nowrap;
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

  nav {
    ul {
      display: flex;
      list-style: none;

      margin-bottom: 1em;
      border-color: var(--medium-color);
      border-width: 1px;

      li {
        border-width: 2px;
        padding: 0.5em 0.8em;

        &.active {
          color: var(--dark-accent-color);
          background-color: var(--medium-color);
          border-color: var(--dark-color);
        }

        &:hover, &:focus {
          color: var(--dark-accent-color);
          border-color: var(--dark-color);
        }
      }

      @media only screen and (min-width: 600px) {
        flex-direction: row;
        border-bottom-style: solid;

        li {
          &.active, &:hover, &:focus {
            border-bottom-style: solid;
          }
        }
      }

      @media only screen and (max-width: 600px) {
        flex-direction: column;
        border-left-style: solid;

        li {
          &.active, &:hover, &:focus {
            border-left-style: solid;
          }
        }
      }
    }
  }

  .page-tab {
    min-height: 45vh;
  }

  ol.item-list {
    list-style: none;
    margin: 1em 0;

    & > li:not(:first-child) {
      margin-top: 1em;
    }
  }
}
</style>
