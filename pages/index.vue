<script setup lang="ts">
import manifest from '~/manifest.json'

type BuildOutcome = "success" | "failure" | "missing"

interface Repository {
  id: string
  fullName: string
  description: string
  url: string
  updatedAt: string
  outcome: BuildOutcome
}

interface Manifest {
  toolchain: string
  matrix: Repository[]
}
</script>

<template>
  <h1>Reservoir</h1>
  <div v-if="manifest !== null">
    <div class="toolchain">
      <span class="label">Latest Toolchain:</span>
      <span class="name">{{ manifest.toolchain }}</span>
    </div>
    <h2>Top {{ manifest.matrix.length }} Repositories</h2>
    <ol>
      <li v-for="repo in manifest.matrix" class="outcome-{{ repo.outcome }}">
        <a :href="repo.url">{{ repo.fullName }}</a>
      </li>
    </ol>
  </div>
  <div v-else>
    <p>Oops! Build data for the repositories is missing.</p>
  </div>
</template>
