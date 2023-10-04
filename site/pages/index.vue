<script setup lang="ts">
import GetStartedIcon from '~icons/mdi/book-open'
import manifest from '~/manifest.json'
const popular = [...manifest.matrix].sort((a, b) =>
  b.stars - a.stars
).slice(0, 10)
const created = [...manifest.matrix].sort((a, b) =>
  new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
).slice(0, 10)
const updated = [...manifest.matrix].sort((a, b) =>
  new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
).slice(0, 10)
definePageMeta({
  layout: false,
});
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
            <h1 class="label">Lake's package repository</h1>
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
              <h4 class="label">Latest Lean Toolchain:</h4>
              <span class="name">{{ manifest.toolchain }}</span>
            </div>
            <a class="get-started" href="https://lean-lang.org/lean4/doc/quickstart.html">
              <GetStartedIcon class="prefix icon"/>
              <span>Get Started with Lean</span>
            </a>
          </div>
          <div class="blurb">
            <p>Reservoir indexes, builds, and tests packages within the Lean and Lake ecosystem.</p>
          </div>
        </div>
        <div class="highlights">
          <HighlightCategory title="Most Popular" :list="popular" to="/packages?sort=stars"/>
          <HighlightCategory title="Newly Created" :list="created" to="/packages?sort=createdAt"/>
          <HighlightCategory title="Recently Updated" :list="updated" to="/packages?sort=updatedAt"/>
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
    }
  }

  .highlights {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;

    .highlight-category {
      @media screen and (max-width: 600px) {
        flex-grow: 1;
        min-width: 0;

        &:not(:first-child) {
          margin-top: 2em;
        }
      }

      @media screen and (min-width: 600px) {
        .card { max-width: 30vw; }
      }
    }
  }
}
</style>
