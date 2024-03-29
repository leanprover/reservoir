<script setup lang="ts">
import NoneIcon from '~icons/mdi/asterisk'
import FailIcon from '~icons/mdi/close'
import PassIcon from '~icons/mdi/check'
import { Tippy } from 'vue-tippy'

const props = defineProps<{build?: Build | null, markOutdated?: boolean}>()
const build = computed<Build | {[_ in keyof Build]?: undefined}>(() => props.build || {});

const outcomeIcon = computed(() => {
  switch (build.value.outcome) {
    case 'success':
      return PassIcon
    case 'failure':
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
  switch (build.value.outcome) {
    case 'success':
      return (outdated.value && props.markOutdated) ? 'outcome-semi-success' : 'outcome-success'
    case 'failure':
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
    <div class="tooltip">
      <span v-if="build.outcome == 'success'">
        Commit {{build.revision.slice(0, 7)}} builds on
        the {{ outdated ? 'old' : 'recent' }} {{build.toolchain}}
        <span v-if="build.requiredUpdate">after <code>lake update</code></span>
      </span>
      <span v-else-if="build.outcome == 'failure'">
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
.build-outcome {
  a, .build-outcome-icon {
    width: 100%;
    height: 100%;
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
