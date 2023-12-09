<script setup lang="ts">
import StarIcon from '~icons/mdi/star'
const props = defineProps<{pkg: Package}>()
const pkg = computed(() => props.pkg)
const src = computed(() => pkg.value.sources.find(src => src.repoUrl))
const build = computed(() =>
  pkg.value.builds.find(b => b.outcome == "success") ??
  pkg.value.builds.find(b => b.toolchain === latestToolchain)
)
</script>

<template>
  <li class="pkg-result card">
    <NuxtLink class="name" :to="`/packages/${encodeURIComponent(pkg.id)}`">
      <h3>{{pkg.fullName}}</h3>
    </NuxtLink>
    <p>
      <span v-if="pkg.description">{{ pkg.description }}</span>
      <em v-else>No description provided.</em>
    </p>
    <ul class="links">
      <li v-if="pkg.homepage">
        <a class="hard-link" :href="pkg.homepage">Homepage</a>
      </li>
      <li v-if="src">
        <a class="hard-link" :href="src.repoUrl">Repository</a>
      </li>
      <li class="stars"><StarIcon class="prefix icon"/>{{ pkg.stars }}</li>
      <li v-if="build" class="build">
        <BuildOutcome class="icon" :build="build"/>
        <span v-if="build.outcome == 'success'" class="toolchain">
          {{ build.toolchain.split(':')[1] }}
        </span>
      </li>
    </ul>
  </li>
</template>

<style lang="scss">
.pkg-result {
  padding: 1em;
  margin-bottom: 1em;

  .name {
    display: block;
    margin-bottom: 0.8em;

    h3 {
      overflow: hidden;
      text-overflow: ellipsis;
      text-wrap: nowrap;
      display: block;
      width: 100%;
    }

    &:hover, &:focus   {
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
