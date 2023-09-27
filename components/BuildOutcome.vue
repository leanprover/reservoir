<script setup lang="ts">
import NoneIcon from '~icons/ion/help'
import FailIcon from '~icons/ion/close'
import PassIcon from '~icons/ion/checkmark'
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

const outcomeTooltip = computed(() => {
  switch (outcome) {
    case 'success':
      return 'Builds on latest toolchain'
    case 'failure':
      return 'Fails to build on latest toolchain'
    default:
      return 'No build data'
  }
})
</script>

<template>
<Tippy :arrow="true" class="build-outcome" :class="[outcomeClass]">
  <component width="66%" height="66%" :is="outcomeIcon"/>
  <template #content>
    <div class="tooltip">{{ outcomeTooltip }}</div>
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
    svg { margin-left: 1%; }
  }

  &.outcome-failure {
    background-color: var(--failure-color);
    svg { margin-left: 1%; margin-top: 1%; }
  }

  &.outcome-none {
    background-color: var(--neutral-color);
    svg { margin-left: 1%; }
  }
}
</style>
