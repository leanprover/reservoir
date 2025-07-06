<template>
  <div class="text-page">
    <div class="page-header">
      <h2>Inclusion Criteria</h2>
    </div>
    <div class="page-body">
      <p>
        Reservoir automatically indexes Lean repositories on GitHub.
        To be included in its selection, a package must meet a few criteria:
      </p>
      <ul>
        <li>
          <b>Public GitHub source repository.</b>
          Reservoir does not index forks or private repositories.
          Repositories generated from a template are considered forks.
        </li>
        <li>
          <b>A root <code>lake-manifest.json</code>.</b>
          There must be a file named exactly <code>lake-manifest.json</code>
          in the top-level directory of the repository.
          Prior to April 2024, Reservoir required a root <code>lakefile.lean</code> instead.
        </li>
        <li>
          <b>GitHub-recognized OSI-approved license.</b>
          GitHub displays the license it detects for a repository on the code
          page in either the right-hand column (desktop) or in the top matter (mobile).
          That license must then be listed as OSI-approved in the
          <a class="hard-link" href="https://spdx.org/licenses/">SPDX License List</a>.
        </li>
        <li>
          <b>At least 2 stars.</b>
          The repository must have at least 2 stars on GitHub.
          This serves as a very basic quality filter.
        </li>
      </ul>
      <p>
        Reservoir updates its index approximately daily.
        If your package meets the above conditions, but does not appear on
        Reservoir after a few days, you can report this as a bug on
        <a class="hard-link" href="https://github.com/leanprover/reservoir/issues">Reservoir's issue tracker</a>.
      </p>
    </div>
  </div>
</template>

<style lang="scss">
.text-page .page-body {
  line-height: 1.7;
  color: var(--color-text);
  font-size: 1.125rem;
  font-weight: 400;

  p {
    margin: 1.5rem 0;
    line-height: 1.6;
    font-size: 1.125rem;
    display: block;
  }

  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    font-weight: 700;
    margin-top: 3rem;
    margin-bottom: 1.5rem;
    line-height: 1.25;
    letter-spacing: -0.015em;
    color: var(--color-text);
  }

  h1 {
    font-size: 2.5rem;
    margin-top: 4rem;
  }

  h2 {
    font-size: 1.8rem;
    margin-top: 3.5rem;
    padding-bottom: 0.7rem;
    border-bottom: 1px solid var(--color-border);
  }

  h3 {
    font-size: 1.5rem;
    margin-top: 2.5rem;
  }

  h4 {
    font-size: 1.25rem;
    margin-top: 2rem;
  }

  h5 {
    font-size: 1.125rem;
    margin-top: 1.5rem;
  }

  h6 {
    font-size: 1rem;
    margin-top: 1.5rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
  }

  strong {
    font-weight: bold;
  }

  a {
    color: var(--color-primary);
    text-decoration: none;
    border-bottom: 1px solid transparent;
    transition: all var(--transition-fast) ease;
    background: linear-gradient(transparent 80%, rgba(56, 110, 224, 0.1) 80%);
  }

  a:hover {
    border-bottom-color: currentColor;
    background: linear-gradient(transparent 70%, rgba(56, 110, 224, 0.2) 70%);
  }

  blockquote {
    padding: 1.5rem 2rem;
    margin: 2rem 0;
    font-style: italic;
    border-radius: 0 8px 8px 0;
    font-size: 1.1rem;
    position: relative;
    border-left: 4px solid var(--color-primary);
    background-color: rgba(56, 110, 224, 0.03);
    color: var(--color-text);
  }

  blockquote::before {
    content: '"';
    font-size: 4rem;
    color: var(--color-primary);
    position: absolute;
    left: 1rem;
    top: -0.5rem;
    opacity: 0.3;
    font-family: Georgia, serif;
  }

  ul, ol {
    padding-left: 2rem;
    margin: 1.5rem 0;

    ul, ol {
      margin-top: 0.75rem;
      margin-bottom: 0;
    }

    li {
      margin-bottom: 0.75rem;
      line-height: 1.6;
    }
  }

  ul {
    list-style-type: disc;
  }

  ul li {
    position: relative;
  }

  ul li::marker {
    color: var(--color-text);
  }

  img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 2.5rem auto;
    border-radius: 12px;
    box-shadow: 0 8px 40px rgba(0, 0, 0, 0.12);
    transition: transform 0.3s ease;
  }

  img:hover {
    transform: scale(1.02);
  }

  code {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 0.4rem;
    font-family: 'JetBrains Mono', 'SF Mono', Monaco, monospace;
    font-size: 1rem;
    position: relative;
    overflow-x: auto;
    color: #1e293b;
    white-space: pre-wrap;
    word-break: break-word;
  }

  pre {
    background: var(--color-bg);
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 1rem;
    overflow-x: auto;
    font-family: 'JetBrains Mono', 'SF Mono', Monaco, monospace;
    font-size: 1rem;
    position: relative;
    margin: 1.5rem 0;
    color: var(--color-text-light);
  }

  pre code {
    background: none;
    border: none;
    padding: 0;
    color: inherit;
    font-size: inherit;
  }

  hr {
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, var(--color-border), transparent);
    margin: 3rem 0;
  }
}

/* Dark theme support */
:root.dark-theme .text-page .page-body {
  color: rgba(255, 255, 255, 0.9);

  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    color: rgba(255, 255, 255, 0.95);
  }

  h2 {
    border-bottom-color: rgba(255, 255, 255, 0.1);
  }

  a {
    color: var(--color-primary-light);
    background: linear-gradient(transparent 80%, rgba(107, 164, 255, 0.1) 80%);
  }

  a:hover {
    background: linear-gradient(transparent 70%, rgba(107, 164, 255, 0.2) 70%);
  }

  blockquote {
    border-left-color: var(--color-primary-light);
    background-color: rgba(107, 164, 255, 0.05);
    color: rgba(255, 255, 255, 0.85);
  }

  blockquote::before {
    color: var(--color-primary-light);
  }

  ul li::marker {
    color: var(--color-primary-light);
  }

  img {
    box-shadow: 0 8px 40px rgba(0, 0, 0, 0.3);
  }

  code {
    background-color: rgba(107, 164, 255, 0.1);
    color: var(--color-text);
    border-color: rgba(107, 164, 255, 0.2);
  }

  pre {
    background-color: #1a1a1a;
    border-color: var(--color-border);
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
  }

  hr {
    background: linear-gradient(to right, transparent, rgba(255, 255, 255, 0.1), transparent);
  }
}

/* Text selection */
.text-page .page-body *::selection {
  background-color: rgba(56, 110, 224, 0.2);
  color: inherit;
}

:root.dark-theme .text-page .page-body *::selection {
  background-color: rgba(107, 164, 255, 0.3);
}

/* Mobile responsiveness */
@media (max-width: 768px) {
  .text-page .page-body {
    font-size: 1.1rem;

    h1 {
      font-size: 2rem;
    }

    h2 {
      font-size: 1.75rem;
    }

    h3 {
      font-size: 1.4rem;
    }

    p {
      margin-bottom: 1.25rem;
    }
  }
}

@media (min-width: 768px) {
  .text-page .page-body p {
    margin-bottom: 1.75rem;
  }
}
</style>
