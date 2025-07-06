<template>
  <NavBar :class="{ active: !isPastTrigger, fixed: true }" />
  <div ref="trigger"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { defineProps } from 'vue';

const props = defineProps({
  enabled: Boolean
});

const trigger = ref(null);
const isPastTrigger = ref(false);
let scrollHandler = null;

const setupScrollListener = () => {
  scrollHandler = () => {
    if (!trigger.value) return;

    const triggerBottom = trigger.value.getBoundingClientRect().bottom;

    if (triggerBottom <= -10 && !isPastTrigger.value) {
      isPastTrigger.value = true;
    } else if (triggerBottom >= -10 && isPastTrigger.value) {
      isPastTrigger.value = false;
    }
  };

  window.addEventListener('scroll', scrollHandler);
};

const removeScrollListener = () => {
  if (scrollHandler) {
    window.removeEventListener('scroll', scrollHandler);
  }
};

onMounted(() => {
  if (props.enabled) {
    setupScrollListener();
  }
});

onUnmounted(() => {
  removeScrollListener();
});

watch(
  () => props.enabled,
  (newVal) => {
    if (newVal) {
      setupScrollListener();
    } else {
      removeScrollListener();
      isPastTrigger.value = false;
    }
  }
);
</script>
