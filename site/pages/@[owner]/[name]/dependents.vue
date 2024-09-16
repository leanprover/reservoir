<script setup lang="ts">
const props = defineProps<{package: Package}>()
const deps = computed(() => props.package.dependents)
const sortOptions: NonEmptyArray<SortOption<PackageDep>> = [
  {label: "Package Name", key: "name", sort: (a, b) => a.name.localeCompare(b.name)},
  {label: "Package Owner", key: "owner", sort(a, b) {
    return a.scope.localeCompare(b.scope) || a.name.localeCompare(b.name)
  }},
]
</script>

<template>
  <div class="dependents-tab">
    <SortedList :items="deps" :itemKey="dep => `${dep.scope}/${dep.name}`" :sortOptions="sortOptions">
      <template #total-label>
        packages depending on <strong class="nowrap">{{ package.fullName }}</strong>
      </template>
      <template #item="{item}">
        <DepItem :upstream="false" :package="package" :dep="item"/>
      </template>
    </SortedList>
  </div>
</template>

<style lang="scss">
.dependents-tab {
  .list-info {

    @media only screen and (max-width: 60em) {
      .displaying { display: none; }
    }

    @media only screen and (max-width: 35em) {
      .total-label { display: none; }
    }
  }
}
</style>
