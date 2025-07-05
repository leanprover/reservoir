<script setup lang="ts">
import NoneIcon from '~icons/mdi/asterisk'
import CalendarIcon from '~icons/mdi/calendar'
import WeightIcon from '~icons/mdi/weight'
import TagIcon from '~icons/mdi/tag'
import { Tippy } from 'vue-tippy'

const props = defineProps<{pkg: Package, ver: PackageVer}>()
const ver = computed(() => props.ver);
const build = computed(() => {
  return props.pkg.builds.find(b => b.toolchain == ver.value.toolchain && b.revision == ver.value.revision)
})

function formatBytes(num: number) {
  for (const unit of ["", "K", "M", "G", "T", "P", "E", "Z"]) {
    if (Math.abs(num) < 1000.0) {
      return `${num.toFixed(1)} ${unit}B`
    }
    num /= 1000.0
  }
  return `${num.toFixed(1)} YB`
}

const verTrack = computed(() => {
  const verId = ver.value.version
  if (!verId) return null
  if (verId === '0.0.0') return null
  const parts = verId.split('.')
  return `${parts[0]}.${parts[0] == '0' ? parts[1] : 'x'}`
})
</script>

<template>
  <li class="version card">
    <div class="version-id">
      <Tippy class="version-track">
        <span v-if="verTrack">{{verTrack}}</span>
        <NoneIcon v-else class="icon"/>
        <template #content>
          <span v-if="verTrack">Version track: {{verTrack}}</span>
          <span v-else>Not a part of any version track.</span>
        </template>
      </Tippy>
      <div class="version-code">
        <code>{{verTrack ? ver.version : ver.revision.slice(0, 7)}}</code>
      </div>
    </div>
    <div class="version-details">
      <div v-if="ver.tag" class="version-detail  version-tag">
        <TagIcon class="icon"/>
        <span>{{ver.tag}}</span>
      </div>
      <div class="version-detail version-date">
        <CalendarIcon class="icon"/>
        <Timestamp prefix="Released on " :time="ver.date"/>
      </div>
      <div class="detail-group">
        <div v-if="ver.toolchain" class="version-detail version-toolchain">
          <BuildOutcome class="icon" :build="build" :packageToolchain="true"/>
          <span class="toolchain">
            {{ ver.toolchain.split(':')[1] }}
          </span>
        </div>
        <div v-if="build && build.archiveSize" class="version-detail version-size">
          <WeightIcon class="icon"/>
          <Tippy>
            <span>{{formatBytes(build.archiveSize)}}</span>
            <template #content>
              Build archive size: {{build.archiveSize}} bytes.
            </template>
          </Tippy>
        </div>
      </div>
    </div>
  </li>
</template>

<style lang="scss">
li.version {
  display: flex;
  flex-direction: row;
  align-items: center;
  padding: 2em 2em;

  .version-id {
    display: flex;
    justify-content: center;
    align-items: center;

    margin-right: 0.8em;

    @media only screen and (min-width: 700px) {
      flex-direction: row;

      .version-track {
        margin-right: 1em;
      }
    }

    @media only screen and (max-width: 700px) {
      flex-direction: column;

      .version-track {
        margin-bottom: 0.8em;
      }
    }
  }

  .version-track {
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;

    width: 2.8em;
    height: 2.8em;
    color: var(--light-text-color);
    background-color: var(--dark-color);
    border-radius: 0.5em;

    .icon {
      width: 1.5em;
      height: 1.5em;
    }
  }

  .version-code {
    font-size: 1em;
  }

  .version-details {
    display: flex;
    flex-direction: row;
    flex-wrap: wrap;
    margin-left: 1em;

    .version-detail {
      display: flex;
      flex-direction: row;
      align-items: center;
      margin-top: 0.25em;
      margin-bottom: 0.25em;
      margin-right: 1em;
    }

    .detail-group {
      display: flex;
      flex-direction: row;
      flex-wrap: wrap;

      .version-detail {
        margin-right: 1em;
      }
    }

    .icon {
      display: inline-block;
      width: 1.2em;
      height: 1.2em;
      margin-right: 0.5em;
    }
  }
}
</style>
