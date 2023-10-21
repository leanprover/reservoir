<script setup lang="ts">
import NoneIcon from '~icons/mdi/asterisk'
import FailIcon from '~icons/mdi/close'
import PassIcon from '~icons/mdi/check'
import { Tippy } from 'vue-tippy'

const props = defineProps<{outcome?: string | null}>()
const outcome = props.outcome

const outcomeIcon = computed(() => {
  switch (outcome) {
    case 'success':
      return PassIcon
    case 'failure':
      return FailIcon
    default:
      return NoneIcon
  }
})

const outcomeClass = computed(() => {
  return 'outcome-' + (outcome || 'none')
})
</script>

<template>
<Tippy class="build-outcome" :class="[outcomeClass]">
  <component width="66%" height="66%" :is="outcomeIcon"/>
  <template #content>
    <div class="tooltip">
      <span v-if="outcome == 'success'">
        Builds on the latest toolchain
      </span>
      <span v-else-if="outcome == 'failure'">
        Builds on the latest toolchain
      </span>
      <span v-else>
        <span class="line">Build data not currently included on Reservoir. </span>
        <span class="line">See the repository's CI instead.</span>
      </span>
    </div>
  </template>
</Tippy>
</template>

<style scoped lang="scss">
.build-outcome {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;

  color: var(--outcome-icon-color);
  border-radius: 50%;

  &.outcome-success {
    background-color: var(--success-color);
  }

  &.outcome-failure {
    background-color: var(--failure-color);
  }

  &.outcome-none {
    background-color: var(--dark-accent-color);
  }
}
</style>
