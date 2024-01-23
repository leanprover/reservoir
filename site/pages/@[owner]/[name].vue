<script setup lang="ts">
import LegalIcon from '~icons/mdi/legal'
import UpdateIcon from '~icons/mdi/update'
import StarIcon from '~icons/mdi/star'
import HomepageIcon from '~icons/mdi/home'
import GitHubIcon from '~icons/mdi/github'

const route = useRoute()
const pkg = packages.find(p => p.owner === route.params.owner && p.name == route.params.name)
if (!pkg) {
  throw createError({
    statusCode: 404,
    message: `Package ${route.params.fullName} not found`,
    fatal: true
  })
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

const buildsByVer = computed(() => {
  const map = pkg.builds.reduce((map, build) => {
    if (!map.has(build.toolchain)) {
      map.set(build.toolchain, build)
    }
    return map;
  }, new Map<string, Build | null>())
  if (!map.has(latestToolchain)) {
    map.set(latestToolchain, null)
  }
  return map
})

const baseContentUrl = computed(() => {
  const githubSrc = pkg.sources.find(src => src.host == 'github')
  if (!githubSrc) return null
  return `https://raw.githubusercontent.com/${githubSrc.fullName}/${githubSrc.defaultBranch}/`
})
const readmeUrl = computed(() => `${baseContentUrl.value}README.md`)
const {data: readme} = await useFetch<string>(readmeUrl)
</script>

<template>
  <div class="package-page">
    <div class="page-header">
      <h2>{{ pkg.name }}</h2>
      <div class="description" v-if="pkg.description">{{ pkg.description }}</div>
    </div>
    <nav>
      <ul>
        <li class="active">Readme</li>
      </ul>
    </nav>
    <div class="page-body">
      <article class="page-main card">
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
            <li v-for="entry in buildsByVer.entries()">
              <BuildOutcome class="icon" :build="entry[1]"/>
              {{ entry[0].split(':')[1] }}
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

    .description {
      margin-top: 0.5em;
    }
  }

  .page-body {
    display: flex;

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
      flex-direction: row;
      list-style: none;

      li {
        padding: 0.5em 0.8em;

        &.active {
          background-color: var(--medium-color);
          border-bottom: 2px solid var(--dark-color);
        }
      }
    }

    border-bottom: 1px solid var(--medium-color);
    margin-bottom: 1em;
  }

  .page-main {
    padding: 1em;
    min-height: 45vh;
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

      li {
        display: flex;
        align-items: center;
        margin-bottom: 0.5em;
      }
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
