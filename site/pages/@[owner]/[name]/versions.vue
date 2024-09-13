<script setup lang="ts">
const props = defineProps<{package: Package}>()
const pkg = computed(() => props.package)

function splitVerLike(ver: string): [number[], string] {
  const dashIdx = ver.indexOf('-')
  const dashEnd = dashIdx < 0 ? ver.length : dashIdx
  const descr = ver.slice(dashEnd+1)
  const verParts = ver.slice(0, dashEnd).split('.').map(p => parseInt(p))
  return [verParts, descr]
}

function versionCompare(a: string, b: string): number {
  const [aVerParts, aDescr] = splitVerLike(a)
  const [bVerParts, bDescr] = splitVerLike(b)
  return arrayCompare(aVerParts, bVerParts, (a, b) => a - b) || aDescr.localeCompare(bDescr)
}

const sortOptions: NonEmptyArray<SortOption<PackageVer>> = [
  {label: "Date", key: "date", sort: (a, b) => b.date.localeCompare(a.date)},
  {label: "Version", key: "version", sort(a, b) {
    const cmp = versionCompare(b.version, a.version)
    return cmp || b.date.localeCompare(a.date)
  }},
  {label: "Tag Version", key: "tag-version", sort(a, b) {
    const cmp = nullishCompare(b.tag, a.tag, (a, b) => versionCompare(a.slice(1), b.slice(1)))
    return cmp || b.date.localeCompare(a.date)
  }},
]
</script>

<template>
  <div class="versions-tab">
    <SortedList :items="pkg.versions" :itemKey="ver => ver.revision" :sortOptions="sortOptions">
      <template #total-label>
        versions of <strong>{{ package.name }}</strong>
      </template>
      <template #item="{item}">
        <VersionItem :pkg="pkg" :ver="item"/>
      </template>
    </SortedList>
  </div>
</template>
