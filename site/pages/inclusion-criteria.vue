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
        </li>
        <li>
          <b>A root <code>lake-manifest.json</code>.</b>
          There mut be a file named exactly <code>lake-manifest.json</code>
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
  line-height: 1.5;

  p {
    margin-bottom: 1em;
  }

  ul, ol {
    margin-left: 2em;
    margin-bottom: 1em;

    ul, ol {
      margin-bottom: 0;
    }

    li {
      margin: 0.5em 0;
    }
  }

  code {
    font-size: 85%;
    padding: 0.2em 0.4em;
    background-color: var(--medium-color);
    border-radius: 6px;
  }
}
</style>
