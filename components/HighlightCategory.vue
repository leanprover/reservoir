<script setup lang="ts">
import { Tippy } from 'vue-tippy'
import ForwardIcon from '~icons/ion/chevron-forward'
const props = defineProps<{title: string, list: any[], to: string}>()
</script>

<template>
  <div class="highlight-category">
    <h3>{{ props.title }}</h3>
    <ol class="short-list">
      <li class="card" v-for="pkg in props.list" :key="pkg.id">
        <BuildOutcome class="icon" :outcome="pkg.outcome"/>
        <Tippy class="text" :on-show="() => { if (!pkg.description) return false }">
          <NuxtLink :to="`/packages/${pkg.id}`">
            <div class="name">{{ pkg.name }}</div>
            <ForwardIcon class="icon"/>
          </NuxtLink>
          <template #content>
            <div class="tooltip">{{ pkg.description }}</div>
          </template>
        </Tippy>
      </li>
    </ol>
    <div class="see-more">
      <NuxtLink :to="props.to">
        <span>See more</span><ForwardIcon class="icon"/>
      </NuxtLink>
    </div>
  </div>
</template>

<style scoped lang="scss">
h3 {
  margin-bottom: 1em;
}

.short-list {
  list-style: none;

  li {
    display: flex;
    flex-direction: row;
    align-items: center;

    margin: 0 0 0.8em 0;
    padding: 1em;

    .text {
      display: flex;
      flex-direction: row;
      align-items: center;
      flex-grow: 1;
      min-width: 0;
    }

    .build-outcome {
      width: 1.2em;
      height: 1.2em;
      margin-right: 0.7em;
    }

    a {
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: space-between;
      flex-grow: 1;
      min-width: 0;

      .name {
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        flex-grow: 1;
      }

      &:hover, &:focus {
        color: var(--light-accent-color);
      }

      &:focus {
        outline: none;
      }

      .icon {
        width: 1em;
        height: 1em;
        margin-left: 0.5em;
      }
    }
  }
}

.see-more {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  margin-top: 1em;

  a {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;

    color: var(--dark-accent-color);

    &:hover, &:focus {
      color: var(--light-accent-color);
    }

    &:focus {
      outline:none;
    }

    .icon {
      width: 1em;
      height: 1em;
      margin-left: 0.5em;
    }
  }
}
</style>
