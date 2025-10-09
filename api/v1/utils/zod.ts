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

export function normalizeToolchain(toolchain: string) {
  if (toolchain === "") {
    return undefined
  }
  let origin, ver
  const colonIdx = toolchain.indexOf(':')
  if (colonIdx < 0) {
    ver = toolchain
    if (ver.startsWith("pr-release-")) {
      origin = "leanprover/lean4-pr-releases"
    } else {
      origin = "leanprover/lean4"
    }
  } else {
    origin = toolchain.slice(0, colonIdx)
    ver = toolchain.slice(colonIdx+1)
  }
  if (ver[0] >= '0' && ver[0] <= '9') {
    ver = `v${ver}`
  }
  return `${origin}:${ver}`
}

export function validatePlatform(platform: string, ctx: z.RefinementCtx) {
  if (platform == "") {
    return undefined
  }
  // The expected legal characters in a target platform.
  // https://stackoverflow.com/questions/13819857/does-a-list-of-all-known-target-triplets-in-use-exist
  if (/^[a-z0-9_\-]+$/.test(platform)) {
    return platform
  } else {
      ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: "Unexpected characters in platform",
      fatal: true,
    });
    return z.NEVER
  }
}
