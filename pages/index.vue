<script setup lang="ts">
import GitHubIcon from '~icons/simple-icons/github'
import LinkedinIcon from '~icons/simple-icons/linkedin'
import ZulipIcon from '~icons/simple-icons/zulip'
import GetStartedIcon from '~icons/ion/book'
import manifest from '~/manifest.json'
useHead({
  title: 'Reservoir',
  meta: [
    { name: 'description', content: 'The Lean package repository.' }
  ]
})
</script>

<template>
  <header>
    <div class="contents">
      <h1 class="title">Reservoir</h1>
    </div>
  </header>
  <main>
    <div class="contents">
      <div class="intro">
        <div class="toolchain">
          <span class="label">Latest Lean Toolchain: </span>
          <span class="name">{{ manifest.toolchain }}</span>
        </div>
        <a href="https://leanprover-community.github.io/get_started.html" class="get-started">
          <GetStartedIcon class="icon"/>
          <span>Get Started with Lean</span>
        </a>
      </div>
      <div class="blurb">
        <p>Reservoir indexes, builds, and tests packages within the Lean and Lake ecosystem.</p>
      </div>
      <h2>{{ manifest.matrix.length }} Indexed Repositories</h2>
      <ol class="matrix">
        <li v-for="repo in manifest.matrix">
          <BuildOutcome class="icon" :outcome="repo.outcome"></BuildOutcome>
          <a :href="repo.url">{{ repo.fullName }}</a>
        </li>
      </ol>
    </div>
  </main>
  <footer>
    <div class="contents">
      <div>
        <h2>Lean</h2>
        <ul>
          <li><a href="https://leanprover.github.io/">Lean Prover</a></li>
          <li><a href="https://lean-fro.org/">The Lean FRO</a></li>
          <li><a href="https://leanprover-community.github.io/">Lean Community</a></li>
          <li><a href="https://github.com/leanprover/lean4/issues">Report a bug</a></li>
        </ul>
      </div>
      <div>
        <h2>Books</h2>
        <ul>
          <li><a href="https://leanprover.github.io/lean4/doc/whatIsLean.html">The Lean Manual</a></li>
          <li><a href="https://leanprover.github.io/theorem_proving_in_lean4/">Theorem Proving in Lean</a></li>
          <li><a href="https://leanprover.github.io/functional_programming_in_lean/">Functional Programming in Lean</a></li>
          <li><a href="https://avigad.github.io/mathematics_in_lean/">Mathematics in Lean</a></li>
        </ul>
      </div>
      <div>
        <h2>Social</h2>
        <ul>
          <li>
            <a href="https://github.com/leanprover">
              <GitHubIcon class="icon"/><span>leanprover</span>
            </a>
          </li>
          <li>
            <a href="https://www.linkedin.com/company/lean-fro">
              <LinkedinIcon class="icon"/><span>Lean FRO</span>
            </a>
          </li>
          <li>
            <a href="https://leanprover.zulipchat.com/">
              <ZulipIcon class="icon"/><span>leanprover</span>
            </a>
          </li>
        </ul>
      </div>
    </div>
  </footer>
</template>

<style lang="scss">
@import url('~/styles/main.scss');
</style>
