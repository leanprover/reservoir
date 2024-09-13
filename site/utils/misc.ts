// Miscellaneous types and utility functions

export interface NonEmptyArray<A> extends Array<A> {
  0: A
}

export function toArray<T>(a: T | T[]) {
  return Array.isArray(a) ? a : [a]
}

export interface SortOption<T> {
  key: string
  label: string
  sort(a: T, b:T): number
}
