import { type Redirect, defineRedirectsModule } from './module'
import { packages, packageAliases, rawPkgLink, pkgLink, findPkg } from '../../utils/manifest'

function oldPkgLink(pkgName: string) {
  const id = pkgName.replace('-', '--').replace('/', '-')
  return `/packages/${encodeURIComponent(id)}`
}

function indexLink(owner: string, name: string, splat: string) {
  return `/index/${encodeURIComponent(owner)}/${encodeURIComponent(name)}/${splat}`
}

let redirects: Redirect[] = []
for (const pkg of packages) {
  redirects.push({
    from: oldPkgLink(pkg.fullName),
    to: rawPkgLink(pkg.owner, pkg.name),
    status: 301,
  })
}
for (const [alias, target] of packageAliases.entries()) {
  const [aliasOwner, aliasName] = alias.split('/')
  const [targetOwner, targetName] = target.split('/')
  const targetPkg = findPkg(targetOwner, targetName)!
  redirects.push({
    from: rawPkgLink(aliasOwner, aliasName),
    to: pkgLink(targetPkg),
    status: 301,
  })
  redirects.push({
    from: oldPkgLink(alias),
    to: pkgLink(targetPkg),
    status: 301,
  })
  redirects.push({
    from: indexLink(aliasOwner, aliasName, '*'),
    to: indexLink(targetOwner, targetName, ':splat'),
    status: 301,
    force: true,
  })
}

export default defineRedirectsModule(redirects)
