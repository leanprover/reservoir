import manifest from '~/manifest.json'

export const packages = manifest.matrix
export type Package = typeof packages[number]
export const latestToolchain = manifest.toolchain
