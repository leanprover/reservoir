import { z } from 'zod'

/**
 * Zod transform to trim extension (e.g., removing `.art` from `abc.art`).
 *
 * If the input has extension, validate it matches `ext` and remove it.
 * If the input does not have an extension, return it verbatim.
 **/
export function trimExt(ext: string, val: string, ctx: z.RefinementCtx) {
  const dotIdx = val.indexOf('.')
  if (dotIdx < 0) return val
  const actualExt = val.slice(dotIdx+1)
  if (actualExt == ext) return val.slice(0, dotIdx)
  ctx.addIssue({
    code: z.ZodIssueCode.custom,
    message: `Expected file extension to be '${ext}', got '${actualExt}'`,
    fatal: true,
  });
  return z.NEVER
}

/** Converts an Lean toolchain into its normal form. */
export function normalizeToolchain(toolchain: string) {
  const colonIdx = toolchain.indexOf(':')
  if (colonIdx < 0) {
    const ver = toolchain
    if (ver[0] == 'v') {
      return `leanprover/lean4:${ver}`
    } else if (ver[0] >= '0' && ver[0] <= '9') {
      return `leanprover/lean4:v${ver}`
    } else if (ver.startsWith("nightly")) {
      return `leanprover/lean4:${ver}`
    } else if (ver.startsWith("pr-release")) {
      return `leanprover/lean4-pr-releases:${ver}`
    } else {
      // In Elan, local toolchains are left as-is whereas others are
      // prefixed with the default origin (Lean's repository).
      // Reservoir (and Lake) cannot distinguish custom toolchains,
      // so they take the simpler route and just leave it as-is.
      return ver
    }
  } else {
    const ver = toolchain.slice(colonIdx+1)
    const origin = toolchain.slice(0, colonIdx)
    if (ver[0] >= '0' && ver[0] <= '9' && origin == 'leanprover/lean4') {
      return `leanprover/lean4:v${ver}`
    // TODO: Normalize nightlies (requires renormalization of indexed toolchains first)
    // } else if (origin == 'leanprover/lean4-nightly' && ver.startsWith("nightly")) {
    //   return `leanprover/lean4:${ver}`
    } else {
      return toolchain
    }
  }
}

/** Converts an optional Lean toolchain into its normal form or `undefined`. */
export function normalizeOptToolchain(toolchain: string) {
  if (toolchain === "") {
    return undefined
  }
  return normalizeToolchain(toolchain)
}

/** Zod transform to validate an optional Lean toolchain. */
export function validateToolchain(toolchain: string, ctx: z.RefinementCtx) {
  if (toolchain === "") {
    return undefined
  }
  const normalized = normalizeToolchain(toolchain)
  if (normalized.length > 256) {
    console.error(`Received toolchain of excessive length ${normalized.length}: ${normalized}`)
    ctx.addIssue({
      code: z.ZodIssueCode.too_big,
      message: "Toolchain bigger than expected",
      type: "string",
      inclusive: true,
      maximum: 100,
      fatal: true,
    });
    return z.NEVER
  }
  // The expected legal characters in a toolchain.
  // Origin should follow GitHub restrictions and we force the version to be similar.
  if (!/^[a-zA-Z0-9_:\/\.\-]+$/.test(normalized)) {
    console.error(`Received toolchain with unexpected characters: ${normalized}`)
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: "Unexpected characters in toolchain",
      fatal: true,
    });
    return z.NEVER
  }
  return normalized
}

/**
 * Converts a toolchain into a single path component by
 * replacing `/` with `--` and `:` with `---` (mirroring Elan).
 */
export function toolchainToDir(toolchain: string) {
  let dir = ""
  for (const c of toolchain) {
    if (c == '/') {
      dir += '--'
    } else if (c == ':') {
      dir += '---'
    } else {
      dir += c
    }
  }
  return dir
}

/** Returns true if `s` is a string of exactly `n` hexadecimal digits. */
export function isFixedHex(s: string, n: number) {
  return s.length == n && /^[a-fA-F0-9]+$/.test(s)
}

/** Zod transform to validate an optional platform target triple. */
// https://stackoverflow.com/questions/13819857/does-a-list-of-all-known-target-triplets-in-use-exist
export function validatePlatform(platform: string, ctx: z.RefinementCtx) {
  if (platform == "") {
    return undefined
  }
  // Target triples are expected to be less than 100 characters.
  // This is validated to avoid overflowing cache keys.
  if (platform.length > 100) {
    console.error(`Received platform of excessive length ${platform.length}: ${platform}`)
    ctx.addIssue({
      code: z.ZodIssueCode.too_big,
      message: "Platform bigger than expected",
      type: "string",
      inclusive: true,
      maximum: 100,
      fatal: true,
    });
    return z.NEVER
  }
  // The expected legal characters in a target triple.
  if (!/^[a-zA-Z0-9_\-]+$/.test(platform)) {
    console.error(`Received platform with unexpected characters: ${platform}`)
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: "Unexpected characters in platform",
      fatal: true,
    });
    return z.NEVER
  }
  return platform
}

/** Zod schema for validating Git revisions */
export const GitRev = z.string()
  .refine(rev => isFixedHex(rev, 40), "Expected revision of exactly 40 hexits")

/* GitHub limits from: https://github.com/dead-claudia/github-limits */

/** Zod schema for validating GitHub repository owner names (e.g., user names, organizations). */
export const GitHubOwner = z.string().min(1).max(39)
  .regex(/^[a-zA-Z0-9\-]+$/, "Unexpected characters in repository owner")

/** Zod schema for validating GitHub repository names names. */
export const GitHubRepo = z.string().min(1).max(100)
  .regex(/^[a-zA-Z0-9_\.\-]+$/, "Unexpected characters in repository name")
  .refine(r => !(r == '.' || r == '..' || r.endsWith(".git")), "Reserved repository name")
