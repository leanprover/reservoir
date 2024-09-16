<script setup lang="ts">
const props = defineProps<{package: Package, version: PackageVer | null | undefined}>()
const deps = computed(() => {
  const deps = props.version?.dependencies ?? []
  return deps.map((dep, idx) => Object.assign({}, dep, {idx: idx}))
})
const sortOptions: NonEmptyArray<SortOption<typeof deps.value[number]>> = [
  {label: "Require Order", key: "require", sort: (a, b) => a.idx - b.idx},
  {label: "Package Name", key: "name", sort: (a, b) => a.name.localeCompare(b.name)},
]
</script>

<template>
  <div class="dependencies-tab">
    <SortedList :items="deps" :itemKey="dep => dep.name" :sortOptions="sortOptions">
      <template #total-label>
        dependencies of <strong>{{ package.name }}</strong>
      </template>
      <template #item="{item}">
        <DepItem :upstream="true" :package="package" :dep="item"/>
      </template>
    </SortedList>
  </div>
</template>
