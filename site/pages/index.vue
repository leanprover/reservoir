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
    <NavBarWatcher :enabled="true"/>
    <header class="gutter">
      <div class="landing-bg"></div>
      <div class="contents">
        <div class="landing-callout">
          <h1 class="label"><strong>This is the Reservoir</strong>, the place for all the Lean packages and documentations</h1>
          <div class="search-bar-container">
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
    <FooterLinks class="contents"/>
  </div>
</template>

<style lang="css" scoped>

header.gutter {
  height: 25rem;
  display: flex;
  position: relative;
}
</style>

<style lang="scss">


.search-bar-container {
  position: absolute;
  bottom: 0;
  width: 100%;
  transform: translateY(50%);
  display: flex;
  justify-content: center;
}


.site-header.fixed {
  position: fixed !important;
}

.site-header.active {
  background-color: transparent !important;
  backdrop-filter: none !important;

  .navbar {
    border: 0px !important;
  }

  .nav-item, .nav-item a, .nav-item svg {
    color: white;
  }

}

header > .contents {
  padding: 0px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: calc(var(--nav-padding-y) * 2 + 1em);
}

.landing-callout {
  display: flex;
  margin: 0px 20px;
  justify-content: center;
  flex-direction: column;
  width: 100%;
  height: 100%;
  position: relative;
  .label {
    text-align: center;
    font-weight: 400;
    font-size: 2.5rem;
  }
}

.landing-bg {
  position: absolute;
  width: 100vw;
  height: 100%;
  left: 0;
  background-image: url('@/assets/background.svg');
  background-size: cover;
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
        flex-direction: row;
        line-height: 1em;
        white-space: nowrap;
        color: var(--light-text-color);
        background-color: var(--color-primary);
        border-radius: var(--radius-md);
        padding: var(--space-4) var(--space-12);
        display: flex;
        align-items: center;
        gap: var(--space-3);
        justify-content: center;
        font-size: var(--fs-md);
        font-weight: 500;
        cursor: pointer;
        transition: all var(--transition-base);

        &:hover, &:focus {
          background-color: var(--color-primary-focus);
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
