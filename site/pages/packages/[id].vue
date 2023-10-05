<script setup lang="ts">
import manifest from '~/manifest.json'
import LegalIcon from '~icons/mdi/legal'
import UpdateIcon from '~icons/mdi/update'
import StarIcon from '~icons/mdi/star'
import HomepageIcon from '~icons/mdi/home'
import GitHubIcon from '~icons/mdi/github'

const route = useRoute()
const pkg = manifest.matrix.find(e => e.id === route.params.id)
if (!pkg) {
  throw createError({
    statusCode: 404,
    message: `Package ${route.params.id} not found`,
    fatal: true
  })
}

useHead({
  title: `${pkg.name} | Reservoir`,
})

const formatLicense = (id: string) => {
  switch (id) {
    case 'apache-2.0':
      return "Apache 2.0"
    case "mit":
      return "MIT"
    default:
      return "Unknown"
  }
}

const baseContentUrl = `https://raw.githubusercontent.com/${pkg.fullName}/HEAD/`
const { data: readme } = await useFetch<string>(`${baseContentUrl}README.md`)
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
        <MarkdownView v-if="readme" :baseUrl="baseContentUrl" prefix="readme:" :value="readme"/>
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
            <a class="soft-link" :href="`${pkg.url}/stargazers`">{{ pkg.stars }} stars</a>
          </li>
        </ul>
        <div>
          <h3>Lean</h3>
          <ul>
            <li>
              <BuildOutcome class="icon" :outcome="pkg.outcome"/>
              {{ manifest.toolchain.split(':')[1] }}
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
          <div>
            <GitHubIcon class="icon"/>
            <a class="hard-link" :href="pkg.url">{{ pkg.fullName }}</a>
          </div>
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
