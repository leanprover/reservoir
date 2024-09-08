<script setup lang="ts">
import NoneIcon from '~icons/mdi/asterisk'
import FailIcon from '~icons/mdi/close'
import PassIcon from '~icons/mdi/check'
import { Tippy } from 'vue-tippy'

const props = defineProps<{build?: Build | null, markOutdated?: boolean, latest?: boolean, packageToolchain?: boolean}>()
const build = computed<Build | {[_ in keyof Build]?: undefined}>(() => props.build || {});

const outcomeIcon = computed(() => {
  switch (build.value.built) {
    case true:
      return PassIcon
    case false:
      return FailIcon
    default:
      return NoneIcon
  }
})

const outdated = computed(() => {
  const buildToolchain = toolchains.find(t => t.name == build.value.toolchain)
  return !buildToolchain || new Date(buildToolchain.date).getTime() < latestCutoff
});

const outcomeClass = computed(() => {
  switch (build.value.built) {
    case true:
      return (outdated.value && props.markOutdated) ? 'outcome-semi-success' : 'outcome-success'
    case false:
      return 'outcome-failure'
    default:
      return 'outcome-none'
  }
})
</script>

<template>
<Tippy class="build-outcome">
  <NuxtLink v-if="build.url" :to="build.url">
    <div class="build-outcome-icon" :class="[outcomeClass]">
      <component width="66%" height="66%" :is="outcomeIcon"/>
    </div>
  </NuxtLink>
  <div v-else class="build-outcome-icon" :class="[outcomeClass]">
    <component width="66%" height="66%" :is="outcomeIcon"/>
  </div>
  <template #content>
    <div class="build-tooltip tooltip">
      <span v-if="build.built === true">
        Commit
        {{build.revision.slice(0, 7)}}
        <span class="latest" v-if="latest">(latest)</span>
        builds on
        {{ packageToolchain ? 'its' : 'the' }}
        {{ outdated ? 'old' : 'recent' }}
        {{ build.toolchain }}
        <span v-if="build.requiredUpdate">
          after <code>lake update</code>
        </span>
      </span>
      <span v-else-if="build.built === false">
        Commit {{build.revision.slice(0, 7)}} fails to build on {{build.toolchain}}
      </span>
      <span v-else>
        <span class="line">Build data not currently included on Reservoir. </span>
        <span class="line">See the package repository's CI instead.</span>
      </span>
    </div>
  </template>
</Tippy>
</template>

<style scoped lang="scss">
.build-tooltip {
  .latest {
    color: var(--light-accent-color);
  }
}

.build-outcome {
  a, .build-outcome-icon {
    width: 100%;
    height: 100%;
  }

  a:focus {
    outline: none;

    .build-outcome-icon {
      outline: solid black;
    }
  }

  .build-outcome-icon {
    display: flex;
    align-items: center;
    justify-content: center;

    border-radius: 50%;
    color: var(--outcome-icon-color);

    &.outcome-success {
      background-color: var(--success-color);
    }

    &.outcome-semi-success {
      background-color: var(--warning-color);
    }

    &.outcome-failure {
      background-color: var(--failure-color);
    }

    &.outcome-none {
      background-color: var(--dark-accent-color);
    }
  }
}
</style>
