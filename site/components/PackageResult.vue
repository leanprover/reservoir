<script setup lang="ts">
import StarIcon from '~icons/mdi/star'
import HomepageIcon from '~icons/mdi/home'
import GitHubIcon from '~icons/mdi/github'
const props = defineProps<{pkg: Package}>()
const pkg = computed(() => props.pkg)
const pkgVer = computed(() => pkg.value.versions.at(0))
const src = computed(() => pkg.value.sources.find(src => src.repoUrl))
const build = computed(() =>
  pkg.value.builds.find(b => b.built) ??
  pkg.value.builds.find(b => b.toolchain === latestToolchain.name)
)
</script>

<template>
  <li class="pkg-result card">
    <div class="heading">
      <NuxtLink class="name" :to="pkgLink(pkg)">
        <h3>{{pkg.owner.replaceAll("-","\u2011")}}/<wbr>{{pkg.name.replaceAll("-","\u2011")}}</h3>
      </NuxtLink>
      <span class="version" v-if="pkgVer && pkgVer.version != '0.0.0'">v{{pkgVer.version}}</span>
    </div>
    <p>
      <span v-if="pkg.description">{{ pkg.description }}</span>
      <em v-else>No description provided.</em>
    </p>
    <ul class="links">
      <li v-if="pkg.homepage">
        <a class="hard-link" :href="pkg.homepage">
          <HomepageIcon class="icon"/>
          <span class="label">Homepage</span>
        </a>
      </li>
      <li v-if="src">
        <a class="hard-link" :href="src.repoUrl">
          <GitHubIcon class="icon"/>
          <span class="label">Repository</span>
        </a>
      </li>
      <li class="stars"><StarIcon class="prefix icon"/>{{ pkg.stars }}</li>
      <li v-if="build" class="build">
        <BuildOutcome class="icon" :build="build"/>
        <span v-if="build.built" class="toolchain">
          {{ build.toolchain.split(':')[1] }}
        </span>
      </li>
    </ul>
  </li>
</template>

<style lang="scss">
.pkg-result {
  padding: 2em;
  margin-bottom: 1em;

  .heading {
    display: flex;
    margin-bottom: 0.8em;

    @media (max-width: 600px) {
      flex-direction: column;

      .version {
        margin-top: 0.3em;
      }
    }

    @media (min-width: 600px) {
      flex-direction: row;
      align-items: baseline;

      wbr {
        display: none;
      }

      .version {
        margin-left: 0.5em;
      }
    }
  }

  .name {
    display: block;
    min-width: 0;

    h3 {
      overflow: hidden;
      text-overflow: ellipsis;
      text-wrap: wrap;
      display: block;
      width: 100%;
    }

    &:hover, &:focus {
      color: var(--light-accent-color);
    }

    &:focus {
      outline: none;
    }
  }

  ul.links {
    list-style: none;

    display: flex;
    flex-direction: row;
    align-items: center;
    margin-top: 1em;

    & > li {
      display: flex;
      margin-right: 0.8em;

      & > a {
        display: flex;
        flex-direction: row;
        align-items: center;

        @media (max-width: 600px) {
          .label { display: none; }
        }

        @media (min-width: 600px) {
          .icon { display: none; }
        }
      }

      &.stars {
        display: flex;
        align-items: center;
        line-height: 1em;

        .icon {
          color: var(--star-color);
        }
      }

      &.build {
        display: flex;
        align-items: center;
        line-height: 1em;

        .toolchain {
          margin-left: 0.5em;
        }
      }

    }
  }
}
</style>
