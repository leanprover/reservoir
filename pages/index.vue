<script setup lang="ts">
import GetStartedIcon from '~icons/ion/book'
import manifest from '~/manifest.json'
const popular = manifest.matrix.slice(0, 10)
const added = [...manifest.matrix].sort((a, b) =>
  new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
).slice(0, 10)
const updated = [...manifest.matrix].sort((a, b) =>
  new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
).slice(0, 10)
</script>

<template>
  <div class="index-page contents">
    <div class="intro">
      <div class="top-line">
        <div class="toolchain">
          <h4 class="label">Latest Lean Toolchain:</h4>
          <span class="name">{{ manifest.toolchain }}</span>
        </div>
        <a href="https://lean-lang.org/lean4/doc/quickstart.html" class="get-started">
          <GetStartedIcon class="icon"/>
          <span>Get Started with Lean</span>
        </a>
      </div>
      <div class="blurb">
        <p>Reservoir indexes, builds, and tests packages within the Lean and Lake ecosystem.</p>
      </div>
    </div>
    <div class="highlights">
      <div>
        <h3>Most Popular</h3>
        <PackageShortList :pkgs="popular"/>
      </div>
      <div>
        <h3>Just Added</h3>
        <PackageShortList :pkgs="added"/>
      </div>
      <div>
        <h3>Recently Updated</h3>
        <PackageShortList :pkgs="updated"/>
      </div>
    </div>
  </div>
</template>

<style lang="scss">
.index-page {
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
        align-items: center;
        text-align: center;
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
        font-size: larger;

        & > .label {
          font-weight: bold;
          margin-right: 0.5em;
        }
        & > .name {
          font-size: 1em;
        }
      }

      .get-started {
        display: flex;
        flex-direction: row;
        align-items: center;

        color: var(--light-text-color);
        background-color: var(--dark-accent-color);
        line-height: 1em;
        padding: 0.5em 2em;

        white-space: nowrap;
        font-family: 'Merriweather', serif;
        border-radius: 12px;

        &:hover {
          background-color: var(--light-accent-color);
        }

        .icon {
          width: 1.5em;
          height: 1.5em;
          margin-right: 1em;
          flex: 0 0 auto;
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
    flex-direction: row;
    justify-content: space-between;
    flex-wrap: wrap;

    @media screen and (max-width: 600px) {
      & > * {
        flex-grow: 1;
      }
    }


    h3 {
      margin-bottom: 1em;
    }

    .short-list {
      margin-bottom: 2em;
    }

    .card  {
      white-space: nowrap;

      @media screen and (min-width: 600px) {
        max-width: 30vw;
      }
    }
  }
}
</style>
