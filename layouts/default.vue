<script setup lang="ts">
import GitHubIcon from '~icons/simple-icons/github'
import LinkedinIcon from '~icons/simple-icons/linkedin'
import ZulipIcon from '~icons/simple-icons/zulip'
import IndexIcon from '~icons/ion/list'
</script>

<template>
  <div class="layout">
    <header>
      <div class="contents">
        <NuxtLink to="/"><h1 class="title">Reservoir</h1></NuxtLink>
        <nav>
          <NuxtLink to="/search" class="all">
            <span class="label">All Packages</span>
            <IndexIcon class="icon"/>
          </NuxtLink>
        </nav>
      </div>
    </header>
    <main>
      <div class="contents">
        <slot/>
      </div>
    </main>
    <footer>
      <div class="contents">
        <div>
          <h2>Lean</h2>
          <ul>
            <li><a href="https://lean-lang.org/">lean-lang.org</a></li>
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
  </div>
</template>
