<script setup lang="ts">
const props = defineProps<{package: Package, version: PackageVer | null | undefined}>()
const transitive = ref(false)
const deps = computed(() => {
  let deps = props.version?.dependencies ?? []
  if (!transitive.value) {
    deps = deps.filter(dep => !dep.transitive)
  }
  return  deps.map((dep, idx) => Object.assign({}, dep, {idx: idx}))
})
const sortOptions: NonEmptyArray<SortOption<typeof deps.value[number]>> = [
  {label: "Require Order", key: "require", sort: (a, b) => a.idx - b.idx},
  {label: "Package Name", key: "name", sort: (a, b) => a.name.localeCompare(b.name)},
]
</script>

<template>
  <div class="dependencies-tab">
    <SortedList :items="deps" :itemKey="dep => dep.name" :sortOptions="sortOptions">
      <template #header>
        <div class="dep-list-info">
          <input id="dep-transitive" v-model="transitive" type="checkbox">
          <label for="dep-transitive">
            <span class="short-label">Transitive</span>
            <span class="long-label">Include transitive dependencies</span>
          </label>
        </div>
      </template>
      <template #item="{item}">
        <DepItem :upstream="true" :package="package" :dep="item"/>
      </template>
    </SortedList>
  </div>
</template>

<style lang="scss">
.dep-list-info {
  display: flex;

  label {
    margin-left: 0.5em;
  }

  @media only screen and (max-width: 50em) {
    .long-label { display: none; }
  }

  @media only screen and (min-width: 40em) {
    .short-label { display: none; }
  }
}
</style>
