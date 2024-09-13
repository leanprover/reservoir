// Miscellaneous types and utility functions

export interface NonEmptyArray<A> extends Array<A> {
  0: A
}

export function toArray<T>(a: T | T[]) {
  return Array.isArray(a) ? a : [a]
}

function arrayCompareFrom<T>(a: T[], b: T[], start: number, compareFn: (a: T, b: T) => number): number {
  if (a.length < start) {
    if (b.length < start) {
      return 0
    } else {
      return -1
    }
  } else if (b.length < start) {
    return 1
  } else {
    return compareFn(a[start], b[start]) || arrayCompareFrom(a, b, start+1, compareFn)
  }
}

/** Orders arrays element-by-element with `compareFn` and by ascending length. */
export function arrayCompare<T>(a: T[], b: T[], compareFn: (a: T, b: T) => number) {
  return arrayCompareFrom(a, b, 0, compareFn)
}

/** Compares non-nullish values with `compareFn`. Nullish values come last. */
export function nullishCompare<T>(a: T | null | undefined, b: T | null | undefined, compareFn: (a: T, b: T) => number) {
  if (a != null) {
    if (b != null) {
      return compareFn(a, b)
    } else {
      return -1
    }
  } else if (b != null) {
    return 1
  } else {
    return 0
  }
}

export interface SortOption<T> {
  key: string
  label: string
  sort(a: T, b: T): number
}
