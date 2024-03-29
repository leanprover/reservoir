<script setup lang="ts">
import GetStartedIcon from '~icons/mdi/book-open'
const popular = [...packages].sort((a, b) =>
  b.stars - a.stars
).slice(0, 10)
const created = [...packages].sort((a, b) =>
  new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
).slice(0, 10)
const updated = [...packages].sort((a, b) =>
  new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
).slice(0, 10)
definePageMeta({
  layout: false,
})
defineOgImage({
  component: 'Generic',
  title: 'Reservoir',
})
</script>

<template>
  <div class="layout">
    <header class="gutter">
      <div class="contents">
        <div class="top-line">
          <Logo/>
          <NavLinks/>
        </div>
        <div class="landing-callout">
          <div class="landing-search">
            <h1 class="label">Lake's package registry</h1>
            <SearchBar/>
          </div>
        </div>
      </div>
    </header>
    <main>
      <div class="landing-page contents">
        <div class="intro">
          <div class="top-line">
            <div class="toolchain">
              <h4 class="label">Latest Lean Stable:</h4>
              <a :href="latestStableToolchain.releaseUrl" class="name">{{ latestStableToolchain.name }}</a>
            </div>
            <a class="get-started" href="https://lean-lang.org/lean4/doc/quickstart.html">
              <GetStartedIcon class="prefix icon"/>
              <span>Get Started with Lean</span>
            </a>
          </div>
          <p class="blurb">
            <span>
              Reservoir indexes, builds, and tests packages within the Lean and Lake ecosystem.
            </span>
            <span>
              If you wish to see your package here, ensure that it meets the
              <NuxtLink class="hard-link" to="inclusion-criteria">Reservoir inclusion criteria</NuxtLink>.
            </span>
          </p>
        </div>
        <div class="highlights">
          <HighlightCategory title="Most Popular" :list="popular" :to="{path: '/packages', query: {sort: 'stars'}}"/>
          <HighlightCategory title="Newly Created" :list="created" :to="{path: '/packages', query: {sort: 'createdAt'}}"/>
          <HighlightCategory title="Recently Updated" :list="updated" :to="{path: '/packages', query: {sort: 'updatedAt'}}"/>
        </div>
      </div>
    </main>
    <footer class="gutter">
      <FooterLinks class="contents"/>
    </footer>
  </div>
</template>

<style lang="scss">
.landing-callout {
  display: flex;
  justify-content: center;
}

.landing-search {
  padding-top: 1em;
  font-size: max(1.5em, min(5vw, 2em));
  margin-bottom: max(1em, min(5vw, 1.5em));

  .label {
    font-size: inherit;
    text-wrap: nowrap;
    margin-bottom: 0.8em;

    @media only screen and (max-width: 500px) {
      padding: 0 3.5vw;
    }

    @media only screen and (min-width: 500px) {
      padding: 0 min(10vw, 4em);
    }
  }

  .search-bar {
    font-size: 0.8em;
  }
}

.landing-page {
  display: flex;
  flex-direction: column;
  margin: 1em 0;

  .intro {
    display: flex;
    flex-direction: column;
    margin-bottom: 2em;

    .top-line {
      display: flex;

      & > * {
        margin-bottom: 1.5em;
      }

      @media only screen and (max-width: 600px) {
        flex-direction: column;
        justify-content: center;
        align-items: center;
      }

      @media screen and (min-width: 600px) {
        flex-direction: row;
        justify-content: space-between;
        align-items: center;

        .toolchain {
          margin-right: 1em;
        }
      }

      .toolchain {
        display: flex;
        flex-direction: column;
        white-space: nowrap;
        font-size: 1.2em;

        & > .label {
          font-weight: bold;
          margin-right: 0.5em;
        }
      }

      .get-started {
        display: flex;
        flex-direction: row;
        align-items: center;

        line-height: 1em;
        padding: 0.5em 2em;
        border-radius: 12px;

        white-space: nowrap;
        font-family: 'Merriweather', serif;

        color: var(--light-text-color);
        background-color: var(--dark-accent-color);
        &:hover, &:focus {
          background-color: var(--light-accent-color);
        }

        &:focus {
          outline: none;
        }

        .icon {
          font-size: 1.5em;
        }
      }
    }

    .blurb {
      @media only screen and (max-width: 600px) {
        text-align: center;
      }

      @media only screen and (min-width: 960px) {
        display: flex;
        flex-wrap: wrap;
      }
    }
  }

  .highlights {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;

    .highlight-category {
      @media screen and (max-width: 650px) {
        width: 100%;

        &:not(:first-child) {
          margin-top: 2em;
        }
      }

      @media screen and (min-width: 650px) {
        .card {
          width: min(320px, 30vw);
        }
      }
    }
  }
}
</style>
