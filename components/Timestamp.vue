<script setup lang="ts">
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import { Tippy } from 'vue-tippy'

dayjs.extend(relativeTime)
const props = defineProps<{prefix?: string, time: string}>();
const time = computed(() => dayjs(props.time))
</script>

<template>
  <Tippy class="timestamp">
    {{  dayjs().to(time) }}
    <template #content>
      <div class="tooltip">
        {{ props.prefix + time.format('MMMM D, YYYY [at] h:mm:ssA') }}
      </div>
    </template>
  </Tippy>
</template>
