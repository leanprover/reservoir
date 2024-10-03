<script setup lang="ts">
import GitHubIcon from '~icons/simple-icons/github'
import XIcon from '~icons/simple-icons/x'
import LinkedinIcon from '~icons/simple-icons/linkedin'
import ZulipIcon from '~icons/simple-icons/zulip'
</script>

<template>
  <div class="footer-links">
    <div>
      <h2 class="group-header">About</h2>
      <ul>
        <li><a href="https://lean-lang.org/">lean-lang.org</a></li>
        <li><a href="https://lean-fro.org/">The Lean FRO</a></li>
        <li><NuxtLink to="/policies/terms">Terms of Use</NuxtLink></li>
        <li><NuxtLink to="/policies/privacy">Privacy Policy</NuxtLink></li>
      </ul>
    </div>
    <div>
      <h2 class="group-header">Explore</h2>
      <ul>
        <li><a href="https://adam.math.hhu.de//">Games</a></li>
        <li><a href="https://live.lean-lang.org/">Playground</a></li>
        <li><a href="https://leanprover-community.github.io/">Community</a></li>
        <li><a href="https://moogle.ai/">Moogle</a></li>
        <li><a href="https://loogle.lean-lang.org/">Loogle</a></li>
      </ul>
    </div>
    <div>
      <h2 class="group-header">Learn</h2>
      <ul>
        <li><a href="https://lean-lang.org/lean4/doc/whatIsLean.html">The Lean Manual</a></li>
        <li><a href="https://lean-lang.org/theorem_proving_in_lean4/">Theorem Proving in Lean</a></li>
        <li><a href="https://lean-lang.org/functional_programming_in_lean/">Functional Programming in Lean</a></li>
        <li><a href="https://avigad.github.io/mathematics_in_lean/">Mathematics in Lean</a></li>
        <li><a href="https://hrmacbeth.github.io/math2001/">The Mechanics of Proof</a></li>
        <li><a href="https://djvelleman.github.io/HTPIwL/">How To Prove It With Lean</a></li>
      </ul>
    </div>
    <div>
      <h2 class="group-header">Social</h2>
      <ul>
        <li>
          <a href="https://github.com/leanprover">
            <GitHubIcon class="prefix icon"/><span>leanprover</span>
          </a>
        </li>
        <li>
          <a href="https://twitter.com/leanprover">
            <XIcon class="prefix icon"/><span>@leanprover</span>
          </a>
        </li>
        <li>
          <a href="https://www.linkedin.com/company/lean-fro">
            <LinkedinIcon class="prefix icon"/><span>Lean FRO</span>
          </a>
        </li>
        <li>
          <a href="https://leanprover.zulipchat.com/">
            <ZulipIcon class="prefix icon"/><span>leanprover</span>
          </a>
        </li>
      </ul>
    </div>
  </div>
</template>

<style lang="scss">
.footer-links {
  display: flex;
  padding: 0.5em 2em 3em 1.5em;

  @media only screen and (max-width: 700px) {
    flex-direction: column;
    justify-content: space-between;
  }

  @media screen and (min-width: 700px) {
    flex-direction: row;
    justify-content: space-around;
  }

  ul {
    list-style: none;

    li {
      display: flex;
      align-items: center;

      padding: 0.3em 0;
      line-height: 1em;
    }
  }

  .group-header {
    margin-top: 1em;
    margin-bottom: 0.5em;
    color: var(--gutter-accent-color);
  }
}
</style>
