<script setup lang="ts">
import LegalIcon from '~icons/mdi/legal'
import UpdateIcon from '~icons/mdi/update'
import StarIcon from '~icons/mdi/star'
import HomepageIcon from '~icons/mdi/home'
import GitHubIcon from '~icons/mdi/github'
import PlusIcon from '~icons/mdi/plus-circle-outline'
import MinusIcon from '~icons/mdi/minus-circle-outline'

const props = defineProps<{package: Package}>()
const pkg = computed(() => props.package)
const pkgVer = computed(() => pkg.value.versions.at(0))

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
  const map = pkg.value.builds.reduce((map, build) => {
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
  const githubSrc = pkg.value.sources.find(src => src.host == 'github')
  if (!githubSrc) return null
  return `https://raw.githubusercontent.com/${githubSrc.fullName}/${githubSrc.defaultBranch}/`
})
const readmeUrl = computed(() => {
  return baseContentUrl.value + (pkgVer.value?.readmeFile ?? 'README.md')
})
const {data: readme} = await useFetch<string>(readmeUrl)
</script>

<template>
  <div class="readme-tab">
    <article class="readme card">
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
</template>

<style lang="scss">
.readme-tab {
  display: flex;

  .card {
    padding: 1em;
  }

  @media only screen and (max-width: 700px) {
    flex-direction: column;

    article {
      margin-bottom: 1em;
    }
  }

  @media screen and (min-width: 700px) {
    flex-direction: row;

    aside {
      max-width: 15em;
      flex: 0 0 auto;
    }

    article {
      min-height: 40em;
      margin-right: 1em;
      flex-grow: 1;
      min-width: 0;
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
