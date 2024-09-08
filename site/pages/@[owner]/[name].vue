<script setup lang="ts">
import LegalIcon from '~icons/mdi/legal'
import UpdateIcon from '~icons/mdi/update'
import StarIcon from '~icons/mdi/star'
import HomepageIcon from '~icons/mdi/home'
import GitHubIcon from '~icons/mdi/github'
import PlusIcon from '~icons/mdi/plus-circle-outline'
import MinusIcon from '~icons/mdi/minus-circle-outline'

const route = useRoute()
const owner = route.params.owner as string
const name = route.params.name as string
const maybePkg = findPkg(owner, name)!
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
  const tab = Array.isArray(route.query.tab) ? route.query.tab.at(-1) : route.query.tab
  return tab ?? 'readme'
})

const pkgVer = computed(() => pkg.versions.at(0))

const formatLicense = (id: string | null) => {
  switch (id && id.toLowerCase()) {
    case 'apache-2.0':
      return "Apache 2.0"
    case "bsd-2-clause":
      return "BSD 2 clause"
    case "bsd-3-clause":
      return "BSD 3 clause"
    case "cc0-1.0":
      return "CC0"
    case "epl-2.0":
      return "EPLv2"
    case "gpl-2.0":
      return "GPLv2"
    case "gpl-3.0":
      return "GPLv3"
    case "agpl-3.0":
      return "AGPLv3"
    case "lgpl-2.1":
      return "LGPLv2.1"
    case "mit":
      return "MIT"
    case "mpl-2.0":
      return "MPLv2"
    case "unlicense":
      return "Unlicense"
    default:
      return "Unknown"
  }
}

type ToolchainBuild = [string, Build | null]
const allToolchainBuilds = computed<ToolchainBuild[]>(() => {
  const map = pkg.builds.reduce((map, build) => {
    if (!map.has(build.toolchain)) {
      map.set(build.toolchain, build)
    }
    return map;
  }, new Map<string, Build | null>())
  const entries = Array(...map.entries())
  if (!map.has(latestToolchain.name)) {
    entries.unshift([latestToolchain.name, null])
  }
  return entries
})
const shortBuildLimit = 10
const shortBuildToggle = ref(allToolchainBuilds.value.length > shortBuildLimit)
const shortToolchainBuilds = computed<ToolchainBuild[]>(() => {
  const filtered = allToolchainBuilds.value.filter(b => {
    return b[0] == pkgVer.value?.toolchain || b[1]?.built
  })
  const list = filtered.length === 0 ? allToolchainBuilds.value : filtered
  return list.slice(0, shortBuildLimit)
})
const toolchainBuilds = computed<ToolchainBuild[]>(() => {
  return shortBuildToggle.value ? shortToolchainBuilds.value : allToolchainBuilds.value
})

const baseContentUrl = computed(() => {
  const githubSrc = pkg.sources.find(src => src.host == 'github')
  if (!githubSrc) return null
  return `https://raw.githubusercontent.com/${githubSrc.fullName}/${githubSrc.defaultBranch}/`
})
const readmeUrl = computed(() => {
  return baseContentUrl.value + (pkgVer.value?.readmeFile ?? 'README.md')
})
const {data: readme} = await useFetch<string>(readmeUrl)
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
          <NuxtLink :to="{path: route.path}">Readme</NuxtLink>
        </li>
        <li v-if="pkg.versions.length > 0" :class="{'active': navTab == 'versions'}">
          <NuxtLink to="?tab=versions">Versions ({{pkg.versions.length}})</NuxtLink>
        </li>
        <li v-if="pkgVer && pkgVer.dependencies.length > 0" :class="{'active': navTab == 'dependencies'}">
          <NuxtLink to="?tab=dependencies">Dependencies ({{pkgVer.dependencies.length}})</NuxtLink>
        </li>
        <li v-if="pkg.dependents.length > 0" :class="{'active': navTab == 'dependents'}">
          <NuxtLink to="?tab=dependents">Dependents ({{pkg.dependents.length}})</NuxtLink>
        </li>
      </ul>
    </nav>
    <div v-if="navTab == 'readme'" class="readme page-body">
      <article  class="page-main readme card">
        <MarkdownView v-if="baseContentUrl && readme" :baseUrl="baseContentUrl" prefix="readme:" :value="readme"/>
        <div v-else><em>No <code>README.md</code> in repository.</em></div>
      </article>
      <aside>
        <ul>
          <li>
            <LegalIcon class="icon"/>
            <span>{{ formatLicense(pkg.license) }}</span>
          </li>
          <li>
            <UpdateIcon class="icon"/>
            <Timestamp prefix="Last updated on " :time="pkg.updatedAt"/>
          </li>
          <li>
            <StarIcon class="icon"/>
            <span>{{ pkg.stars }} stars</span>
          </li>
        </ul>
        <div>
          <h3>Lean</h3>
          <ul>
            <li v-for="[toolchain, build] in toolchainBuilds" :key="toolchain" :class="{'package-toolchain': pkgVer?.toolchain == toolchain}">
              <BuildOutcome class="icon" :build="build" :latest="pkgVer && pkgVer.revision == build?.revision" :packageToolchain="pkgVer?.toolchain == toolchain"/>
              {{ toolchain.split(':')[1] }}
            </li>
            <li v-if="shortToolchainBuilds.length < allToolchainBuilds.length" @click="shortBuildToggle = !shortBuildToggle" >
              <a class="hard-link" tabindex="0" @keyup.enter="shortBuildToggle = !shortBuildToggle">
                <component :is="shortBuildToggle ? PlusIcon : MinusIcon" class="icon"></component>
                <span>
                  {{ allToolchainBuilds.length - shortToolchainBuilds.length }}
                  {{ shortBuildToggle ? 'more' : 'less' }}
                </span>
              </a>
            </li>
          </ul>
        </div>
        <div class="main-link" v-if="pkg.homepage">
          <h3>Homepage</h3>
          <div>
            <HomepageIcon class="icon"/>
            <a class="hard-link" :href="pkg.homepage">{{ pkg.homepage.split('://')[1] }}</a>
          </div>
        </div>
        <div class="main-link">
          <h3>Repository</h3>
          <template v-for="src in pkg.sources" :key="src.id">
            <div v-if="src.host === 'github'">
              <GitHubIcon class="icon"/>
              <a class="hard-link" :href="src.repoUrl">{{ src.fullName }}</a>
            </div>
          </template>
        </div>
      </aside>
    </div>
    <div v-if="navTab == 'versions'" class="versions page-body">
      <ol class="versions-list">
        <VersionItem v-for="ver in pkg.versions" :key="ver.revision" :pkg="pkg" :ver="ver"/>
      </ol>
    </div>
    <div v-if="navTab == 'dependencies'" class="dependencies page-body">
      <ol class="dependencies-list">
        <DepItem :upstream="true" v-for="dep in pkgVer!.dependencies!" :key="dep.name" :dep="dep"/>
      </ol>
    </div>
    <div v-if="navTab == 'dependents'" class="dependents page-body">
      <ol class="dependents-list">
        <DepItem :upstream="false" v-for="dep in pkg.dependents" :key="dep.name" :dep="dep"/>
      </ol>
    </div>
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

  .readme.page-body {
    display: flex;

    .card {
      padding: 1em;
    }

    @media only screen and (max-width: 700px) {
      flex-direction: column;
      .page-main {
        margin-bottom: 1em;
      }
    }

    @media screen and (min-width: 700px) {
      flex-direction: row;

      aside {
        max-width: 15em;
        flex: 0 0 auto;
      }

      .page-main {
        min-height: 40em;
        margin-right: 1em;
        flex-grow: 1;
        min-width: 0;
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

  .page-main {
    min-height: 45vh;
  }

  .page-body {
    ol {
      list-style: none;
      margin: 1em 0;

      & > li:not(:first-child) {
        margin-top: 1em;
      }
    }
  }

  aside {
    h3 {
      margin-bottom: 0.8em;
    }

    & > * {
      margin-top: 1em;
    }

    .icon {
      width: 1.2em;
      height: 1.2em;
      margin-right: 0.5em;
      flex: 0 0 auto;
    }

    ul {
      list-style: none;

      li, a {
        display: flex;
        align-items: center;
        margin-bottom: 0.5em;
      }
    }

    .package-toolchain {
      font-weight: bold;
    }

    .main-link {
      & > div {
        display: flex;
        flex-direction: row;
        align-items: center;
        white-space: nowrap;

        a {
          overflow: hidden;
          text-overflow: ellipsis;
          display: block;
        }
      }
    }
  }
}
</style>
