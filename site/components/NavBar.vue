<script setup lang="ts">
import IndexIcon from '~icons/mdi/lake'
import ReservoirIcon from '~/assets/reservoir.svg?component'

import GithubIcon from '~/assets/github.svg'
import MoonrIcon from '~/assets/moon-outline.svg'

</script>

<template>
  <header class="site-header">
    <nav class="navbar" role="navigation" aria-label="Primary navigation">
      <div class="navbar-container container">
        <NuxtLink class="nav-logo" to="/">
          <Logo />
        </NuxtLink>

        <div class="nav-toggle">
          <input type="checkbox" id="nav-toggle" class="nav-toggle-checkbox" />
          <label for="nav-toggle" class="nav-toggle-label" aria-label="Toggle navigation menu">☰</label>
        </div>

        <ul class="desktop-menu">
          <div class="desktop-menu-part">
            <li class="nav-item"><NuxtLink to="/packages" class="nav-link">All Packages</NuxtLink></li>
            <li class="nav-item"><NuxtLink to="/inclusion-criteria" class="nav-link">Terms</NuxtLink></li>
          </div>

          <div class="desktop-menu-part">
            <li class="nav-item">
              <a href="https://github.com/leanprover/reservoir" class="nav-link" target="_blank" rel="noopener noreferrer">
                <GithubIcon />
              </a>
            </li>
          </div>
        </ul>
      </div>

      <ul class="mobile-nav">
        <ul class="nav-list">
          <li class="nav-item"><NuxtLink to="/install" class="nav-link">Install</NuxtLink></li>
          <li class="nav-item"><NuxtLink to="/learn" class="nav-link">Learn</NuxtLink></li>
          <li class="nav-item"><NuxtLink to="/community" class="nav-link">Community</NuxtLink></li>
          <li class="nav-item"><NuxtLink to="/use-cases" class="nav-link">Use Cases</NuxtLink></li>
          <li class="nav-item"><a href="https://live.lean-lang.org/" class="nav-link" target="_blank">Playground</a></li>
          <li class="nav-item"><a href="https://reservoir.lean-lang.org/" class="nav-link" target="_blank">Reservoir</a></li>
          <li class="nav-item"><NuxtLink to="/blog" class="nav-link">Blog</NuxtLink></li>
        </ul>
      </ul>
    </nav>
  </header>
</template>

<style scoped lang="scss">

.site-header {
  position: sticky;
  top: 0;
  z-index: var(--z-header);
  background-color: var(--color-bg-translucent);
  backdrop-filter: blur(10px);
  transition: background-color var(--transition-base), border-color var(--transition-base);
  width: 100%;


  @media (max-width: 1024px) {
    background-color: var(--color-bg);
  }
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--nav-padding-y) var(--space-8);
  border-bottom: 1px solid var(--color-border);
  box-sizing: border-box;
  width: 100%;

  @media (max-width: 768px) {
    padding: var(--space-1) var(--space-2);
  }

  .navbar-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    max-width: min(1080px, 100vw);
  }

  .nav-logo {
    display: flex;
    align-items: center;
    margin-right: var(--space-6);
    font-size: 25px;
    color: var(--color-text);
    font-weight: 300;
    text-decoration: none;
    
    img,
    svg {
      vertical-align: middle;
      width: 100px;
      margin: 0px !important;
    }
  }

  .nav-toggle {
    display: none;
    align-items: center;

    &-checkbox {
      display: none;
    }

    &-label {
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      padding: var(--space-3);
      font-size: var(--fs-xl);
      color: var(--color-text);
      transition: all var(--transition-base);
    }

    @media (max-width: 1024px) {
      display: flex;
    }
  }

  .desktop-menu {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    list-style: none;
    margin: 0;
    padding: 0;
    gap: var(--space-6);

    @media (max-width: 1024px) {
      display: none;
    }

    &-part {
      display: flex;
      align-items: center;
      gap: var(--gap-sm);
      list-style: none;
      margin: 0;
      padding: 0;
    }
  }

  .mobile-nav {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background-color: var(--color-bg);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--color-border);
    padding: var(--space-4) var(--space-8);
    z-index: 100;

    .nav-list {
      display: flex;
      flex-direction: column;
      gap: 0;
      list-style: none;
      margin: 0;
      padding: 0;

      .nav-item {
        margin: var(--space-2) 0;
        width: 100%;

        .nav-link {
          width: 100%;
          display: block;
          justify-content: flex-start;
          padding: var(--space-4);
        }
      }

      .has-submenu {
        display: block;

        .fro-toggle-checkbox {
          display: none;
        }

        > .nav-link {
          justify-content: space-between;
          position: relative;
          width: 100%;

          &::after {
            content: '▸';
            transition: transform 0.3s;
          }
        }

        .fro-toggle-checkbox:checked + .nav-link::after {
          transform: rotate(90deg);
        }

        .submenu {
          display: none;
          flex-direction: column;
          padding-left: var(--space-4);
        }

        .fro-toggle-checkbox:checked + .nav-link + .submenu {
          display: flex;
        }
      }
    }

    @media (max-width: 1024px) {
      display: none;

      .nav-toggle-checkbox:checked ~ & {
        display: block;
      }

      .navbar:has(.nav-toggle-checkbox:checked) & {
        display: block;
      }
    }
  }
}

.nav-item {
  display: flex;
  align-items: center;
  list-style: none;

  &.active .nav-link {
    background-color: rgb(102 142 226 / 12%);
    color: var(--color-primary);
  }
  
  &.active .nav-link svg {
    fill: var(--color-primary);
  }
}

.nav-link {
  text-decoration: none;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text);
  font-weight: 500;
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-md);
  transition: all var(--transition-base);
  border: none;
  background: transparent;
  position: relative;
  font-size: 0.9rem;
  cursor: pointer;
  transform: translateY(0);
  white-space: nowrap;

  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background: var(--color-hover);
    border-radius: var(--radius-md);
    opacity: 0;
    transition: opacity var(--transition-base);
    z-index: -1;
  }

  &:hover {
    color: var(--color-primary);

    &::before {
      opacity: 1;
    }
  }

  svg {
    width: 20px;
    height: 20px;
  }
}

.sub-navbar {
  display: flex;
  align-items: center;
  padding: var(--space-2) var(--space-8);
  border-bottom: 1px solid var(--color-border);
  box-sizing: border-box;

  @media (max-width: 1024px) {
    display: none;
  }

  .navbar-container {
    justify-content: start;
  }
}

.nav-list {
  display: flex;
  align-items: center;
  gap: var(--gap-sm);
  list-style: none;
  margin: 0;
  padding: 0;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}

.dark-theme {
  .navbar {
    fill: white;
    stroke: white;
  }

  .nav-link svg {
    fill: var(--color-text);
    stroke: var(--color-text);
  }
}
</style>
