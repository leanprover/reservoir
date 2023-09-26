<script setup lang="ts">
import manifest from '~/manifest.json'
import StarIcon from '~icons/ion/star'
</script>

<template>
  <div class="search-page contents">
    <div class="page-header">
      <h2>All Packages</h2>
    </div>
    <div class="results">
      <div class="results-header">
        <div>Displaying <strong>{{ manifest.matrix.length }}</strong> results</div>
        <div class="sort-by">
          <span class="label">Sort by</span>
          <span class="dropdown">Most Popular</span>
        </div>
      </div>
      <ol class="results-list">
        <li class="card" v-for="repo in manifest.matrix" :key="repo.id">
          <h3>{{repo.fullName}}</h3>
          <p>{{repo.description}}</p>
          <ul class="links">
            <li v-if="repo.homepage"><a :href="repo.homepage">Homepage</a></li>
            <li><a :href="repo.url">Repository</a></li>
            <li class="stars"><StarIcon class="icon"/>{{ repo.stars }}</li>
            <li><BuildOutcome :outcome="repo.outcome"/></li>
          </ul>
        </li>
      </ol>
    </div>
  </div>
</template>

<style lang="scss">
.search-page {
  .page-header {
    padding: 1em;
    background-color: #ebedf1;
    border-radius: 6px;
    margin-bottom: 1em;
  }

  .results {
    .results-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .sort-by {
        display: flex;
        align-items: center;

        .label {
          margin-right: 0.5em;
        }

        .dropdown {
          padding: 0.5em 0.8em;
          background-color: #ebedf1;
          border-radius: 6px;
        }
      }
    }

    ol.results-list {
      list-style: none;
      margin: 1em 0;

      & > li {
        padding: 1em;
        margin-bottom: 1em;

        h3 {
          margin-bottom: 0.8em;
        }

        ul.links {
          list-style: none;

          display: flex;
          flex-direction: row;
          align-items: center;
          margin-top: 1em;

          & > li {
            margin-right: 0.8em;

            a {
              color: var(--dark-accent-color);

              &:hover {
                color: var(--light-accent-color);
              }
            }

            &.stars {
              display: flex;
              align-items: center;
              .icon {
                width: 1em;
                height: 1em;
                color: var(--star-color);
                margin-right: 0.5em;
              }
            }

            .build-outcome {
              width: 1em;
              height: 1em;
            }
          }
        }
      }
    }
  }
}
</style>
