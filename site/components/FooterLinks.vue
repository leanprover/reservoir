<script setup lang="ts">
import GitHubIcon from '~icons/simple-icons/github'
import XIcon from '~icons/simple-icons/x'
import LinkedinIcon from '~icons/simple-icons/linkedin'
import ZulipIcon from '~icons/simple-icons/zulip'
import MastodonIcon from '~icons/simple-icons/mastodon'
import BlueskyIcon from '~icons/simple-icons/bluesky'

import LeanIcon from '~/assets/white-logo.svg'

</script>

<template>
  <footer role="contentinfo" aria-label="Site footer" class="footer">
    <div class="footer-grid container">
      <nav class="footer-column" aria-label="LEAN">
        <LeanIcon class="lean-icon" width="100" height="100"/>
      </nav>

      <nav class="footer-column" aria-label="LEAN">
        <h3 id="get-started" class="footer-heading">Get Started</h3>
        <ul class="footer-links">
          <li><a href="/install" class="footer-text">Install</a></li>
          <li><a href="/learn" class="footer-text">Learn</a></li>
          <li><a href="/community" class="footer-text">Community</a></li>
          <li><a href="/reservoir" class="footer-text">Reservoir</a></li>
        </ul>
      </nav>

      <nav class="footer-column" aria-label="Documentation">
        <h3 id="documentation" class="footer-heading">Documentation</h3>
        <ul class="footer-links">
          <li><a href="/doc/reference/latest/" class="footer-text">Reference manual</a></li>
          <li><a href="/language-reference" class="footer-text">Language reference</a></li>
          <li><a href="/use-cases" class="footer-text">Use cases</a></li>
          <li><a href="/learn#how-to-cite-lean" class="footer-text">Cite lean</a></li>
        </ul>
      </nav>

      <nav class="footer-column" aria-label="Resources">
        <h3 id="resources" class="footer-heading">Resources</h3>
        <ul class="footer-links">
          <li><a href="https://live.lean-lang.org/" class="footer-text">Lean playground</a></li>
          <li>
            <a
              href="https://marketplace.visualstudio.com/items?itemName=leanprover.lean4"
              class="footer-text"
            >
              VSCode extension
            </a>
          </li>
          <li><a href="https://loogle.lean-lang.org/" class="footer-text">Loogle</a></li>
          <li><a href="https://github.com/leanprover-community/mathlib4" class="footer-text">Mathlib</a></li>
        </ul>
      </nav>

      <nav class="footer-column" aria-label="FRO">
        <h3 id="fro" class="footer-heading">FRO</h3>
        <ul class="footer-links">
          <li><a href="/fro#mission" class="footer-text">Mission</a></li>
          <li><a href="/fro/team" class="footer-text">Team</a></li>
          <li><a href="/fro/advisors" class="footer-text">Advisors</a></li>
          <li><a href="/contact" class="footer-text">Contact</a></li>
        </ul>
      </nav>

      <nav class="footer-column" aria-label="Policies">
        <h3 class="footer-heading">Policies</h3>
        <ul class="footer-links">
          <li><a href="/privacy" class="footer-text">Privacy Policy</a></li>
          <li><a href="/terms-of-use" class="footer-text">Terms of Use</a></li>
          <li><a href="/logo-policy" class="footer-text">Lean Logo Policy</a></li>
        </ul>
      </nav>
    </div>

    <div class="footer-divider container" role="separator"></div>

    <div class="footer-bottom container">
      <div class="footer-copy">© 2025 Lean FRO. All rights reserved.</div>
      <div class="footer-socials">
        <label class="theme-switch">
          <input type="checkbox" class="change-theme" />
          <span class="slider"></span>
        </label>
        <a><MastodonIcon /></a>
        <a><BlueskyIcon /></a>
        <a><ZulipIcon /></a>
        <a><XIcon /></a>
      </div>
    </div>
  </footer>
</template>

<style scoped>

.lean-icon {
  width: 80px;
  height: 40px;
}

footer {
  background-color: var(--color-primary);
  color: var(--color-text-contrast);
  padding: var(--space-4);
  font-family: var(--font-primary);
  transition: background-color var(--transition-base);
  margin-top: 50px;
}

.footer-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: var(--space-10);
  margin: var(--space-8) auto;
  box-sizing: border-box;
}

.footer-column {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: var(--space-8);
  padding-bottom: var(--space-12);
  font-size: var(--fs-sm);
  box-sizing: border-box;
}

.footer-heading {
  font-size: var(--fs-sm);
  margin-bottom: var(--space-2);
  color: var(--color-text-contrast);
}

.footer-text {
  font-size: var(--fs-sm);
  color: var(--color-text-contrast);
  line-height: 1.4;
}

.footer-links li {
  padding-bottom: 0.5rem;
  list-style-type: none;
}

.footer-links {
  display: flex;
  flex-direction: column;
}

.footer-logo {
  width: 80px;
  filter: brightness(0) invert(1);
}

.footer-divider {
  border-top: 1px solid #ffffff1c;
  padding: 0;
}

.footer-socials {
  display: flex;
  gap: 20px;
}

.theme-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.theme-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  background-color: #ccc;
  border-radius: 34px;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  transition: background-color 0.3s;
}

.slider::before {
  content: "";
  position: absolute;
  height: 20px;
  width: 20px;
  left: 4px;
  bottom: 2px;
  background-color: white;
  border-radius: 50%;
  transition: transform 0.3s;
}

input:checked + .slider {
  background-color: #4a90e2;
}

input:checked + .slider::before {
  transform: translateX(22px);
}

@media (max-width: 768px) {
  .footer-grid {
    grid-template-columns: repeat(1, 1fr);
  }

  .footer-bottom {
    flex-direction: column;
    gap: 30px;
  }

  .footer-socials {
    gap: 0px;
    justify-content: space-between;
    width: 100%;
  }
}
</style>
