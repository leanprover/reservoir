<script setup lang="ts">
import {unified} from 'unified'
import remarkParse from 'remark-parse'
import remarkGfm from 'remark-gfm'
import remarkGemoji from 'remark-gemoji'
import remarkMath from 'remark-math'
import remarkRehype from 'remark-rehype'
import rehypeRaw from 'rehype-raw'
import rehypeSanitize from 'rehype-sanitize'
import rehypeMathjax from 'rehype-mathjax/svg'
import rehypeExternalLinks from 'rehype-external-links'
import rehypeSlug from 'rehype-slug'
import rehypeAutolinkHeadings from 'rehype-autolink-headings'
import rehypeHighlight from 'rehype-highlight'
import rehypeStringify from 'rehype-stringify'

import type * as HAST from 'hast'
import type * as MDAST from 'mdast'
import {visit} from 'unist-util-visit'
// @ts-ignore for some reason TS does not recognize the package's types
import {classnames} from 'hast-util-classnames'

const props = defineProps<{value: string, baseUrl: string, prefix?: string}>()
const html = computed(() => {
  const ensureBaseUrl = (node: HAST.Element, urlProp: string) => {
    const url = node.properties[urlProp]
    if (typeof url === 'string') {
      node.properties[urlProp] = new URL(url, props.baseUrl).toString()
    }
  }
  return unified()
  .use(remarkParse)
  .use(remarkGfm)
  .use(remarkGemoji)
  .use(remarkMath)
  .use(() => (tree: MDAST.Root) => visit(tree, (node) => {
    // bump all headings by 1 (e.g., h1 -> h2)
    if (node.type === 'heading') node.depth++
  }))
  .use(remarkRehype, {allowDangerousHtml: true}) // allow it, then sanitize it below
  .use(rehypeRaw)
  .use(rehypeSanitize)
  .use(rehypeMathjax)
  .use(() => (tree: HAST.Root) => visit(tree, 'element', (node) => {
    // style markdown lines as hard links
    if (node.tagName === 'a')
      classnames(node, 'hard-link')
    // ensure no relative URLs appear
    ensureBaseUrl(node, 'href')
    ensureBaseUrl(node, 'src')
  }))
  .use(rehypeExternalLinks)
  .use(rehypeSlug, {prefix: props.prefix})
  .use(rehypeAutolinkHeadings, {behavior: 'wrap'})
  .use(rehypeHighlight, {detect: true, languages: {lean}})
  .use(rehypeStringify)
  .processSync(props.value)
})
</script>

<template>
<div class="markdown" v-html="html"></div>
</template>

<style lang="scss">
@import url('highlight.js/styles/github.css');

.markdown {
  overflow-x: auto;
  overflow-y: hidden;

  line-height: 1.5;
  margin: 0.5em;

  h2 {
    border-bottom: 1px solid var(--medium-color);
  }

  h1, h2, h3, h4, h5, h6 {
    padding: 0.3em 0;
    margin: 0.5em 0;
    color: inherit;

    a {
      &:hover, &:focus {
        color: var(--light-accent-color);
      }

      &:focus {
        outline: none;
      }
    }
  }

  table, th, td {
    border-collapse: collapse;
    border: 1px solid var(--medium-color);
  }

  th, td {
    padding: 0.4em 0.8em;
  }

  & > *:first-child {
    padding-top: 0;
    margin-top: 0;
  }

  & > *:last-child {
    margin-bottom: 0;
  }

  img {
    max-width: 100% !important;
  }

  pre {
    margin: 1em 0;
    background-color: var(--medium-color);
    border-radius: 6px;
  }

  ul, ol, p, img {
    margin-bottom: 1em;
  }

  p img {
    margin-bottom: 0;
  }

  ul, ol {
    margin-left: 2em;

    ul, ol {
      margin-bottom: 0;
    }

    li {
      margin: 0.5em 0;
    }
  }

  .contains-task-list {
    position: relative;
  }

  .task-list-item {
    list-style-type: none;

    input {
      margin-left: -1.5em;
      margin-right: 0.2em;
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
