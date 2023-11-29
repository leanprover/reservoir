import manifest from '~/manifest.json'

export const packages = manifest.packages
export type Package = typeof packages[number]
export type Build = Package['builds'][number]
export const latestToolchain = manifest.toolchains[0]
