import manifest from '../manifest.json'

export interface GitSource {
  gitUrl: string
}

export interface RepoSource {
  repoUrl: string
}

export interface GitHubSource extends GitSource, RepoSource {
  host: 'github'
  id: string
  fullName: string
}

export type Source = GitHubSource

export interface Build {
  url?: string
  builtAt: string
  revision: string
  toolchain: string
  requiredUpdate?: boolean
  outcome: string
}

export interface Package {
  name : string
  owner: string
  fullName: string
  description: string | null
  homepage: string | null
  license: string | null
  createdAt: string
  updatedAt: string
  stars: number
  sources: Source[]
  builds: Build[]
}

export const packages = manifest.packages as Package[]
export const latestToolchain: string = manifest.toolchains[0]

export const pkgLink = (pkg: Package) => {
  return `/@${encodeURIComponent(pkg.owner)}/${encodeURIComponent(pkg.name)}`
}
