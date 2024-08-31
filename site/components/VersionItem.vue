<script setup lang="ts">
import StarIcon from '~icons/mdi/star'
import CalendarIcon from '~icons/mdi/calendar'
import WeightIcon from '~icons/mdi/weight'
import TagIcon from '~icons/mdi/tag'

const props = defineProps<{pkg: Package, ver: PackageVer}>()
const build = computed(() => {
  return props.pkg.builds.find(b => b.toolchain == props.ver.toolchain && b.revision == props.ver.revision)
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

</script>

<template>
  <li class="version card">
    <div class="version-id">
      <div class="version-track">
        <StarIcon v-if="ver.version === '0.0.0'" class="icon"/>
        <span v-else>{{ver.version}}</span>
      </div>
      <div class="version-code">
        <code>{{ver.version == '0.0.0' ? ver.revision.slice(0, 7) : ver.version}}</code>
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
          <BuildOutcome class="icon" :build="build"/>
          <span class="toolchain">
            {{ ver.toolchain.split(':')[1] }}
          </span>
        </div>
        <div v-if="build && build.archiveSize" class="version-detail version-size">
          <WeightIcon class="icon"/>
          <span>{{formatBytes(build.archiveSize)}}</span>
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
  padding: 1em 1.5em;

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
