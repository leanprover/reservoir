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
