import manifest from '../manifest.json'

export interface GitSource {
  type: 'git'
  gitUrl: string
  defaultBranch?: string
  subDir?: string
}

export interface RepoSource {
  repoUrl: string
}

export interface GitHubSource extends GitSource, RepoSource {
  host: 'github'
  id: string
  fullName: string
  defaultBranch: string
}

export type Source = GitHubSource

export interface Build {
  url?: string | null
  runAt: string
  revision: string
  toolchain: string
  built: boolean | null
  tested: boolean | null
  requiredUpdate?: boolean | null
  archiveSize?: number | null
}

export interface PackageDep {
  type: string
  name: string
  scope: string
  version: string
  rev: string | null
}

export interface PackageVer {
  version: string | null
  revision: string
  date: string
  tag: string | null
  toolchain: string | null
  dependencies: PackageDep[]
  license: string
  licenseFiles:  string[]
  readmeFile: string | null
}

export interface Package {
  name: string
  owner: string
  fullName: string
  description: string | null
  keywords: string[]
  homepage: string | null
  license: string | null
  createdAt: string
  updatedAt: string
  stars: number
  sources: Source[]
  versions: PackageVer[]
  dependents: PackageDep[]
  builds: Build[]
}

export interface Toolchain {
  name: string
  version: number | null
  tag: string
  date: string
  releaseUrl: string
  prerelease: boolean
}

export const packages = manifest.packages as Package[]
export const packageAliases = new Map<string, string>(Object.entries(manifest.packageAliases))
export const toolchains = manifest.toolchains as Toolchain[]
export const latestToolchain = toolchains[0]
export const latestStableToolchain = toolchains.find(t => !t.prerelease) ?? latestToolchain
export const oldestStableVerToolchain = toolchains.findLast(t => t.version == latestStableToolchain.version) ?? latestToolchain
export const latestCutoff = new Date(oldestStableVerToolchain.date).getTime()

export function findPkg(owner: string, name: string) {
  return packages.find(p => {
    return p.owner.toLowerCase() === owner.toLowerCase() &&
      p.name.toLowerCase() == name.toLowerCase()
  })
}

export function rawPkgLink(owner: string, name: string) {
  return `/@${encodeURIComponent(owner)}/${encodeURIComponent(name)}`
}

export function pkgLink(pkg: Package) {
  return rawPkgLink(pkg.owner, pkg.name)
}
