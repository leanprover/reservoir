import { defineRedirectsModule } from './module'
import { type Package, packages, pkgLink } from '../../utils/manifest'

const oldPkgLink = (pkg: Package) => {
  const id = pkg['fullName'].replace('-', '--').replace('/', '-')
  return `/packages/${encodeURIComponent(id)}`
}

export default defineRedirectsModule(packages.map(pkg => ({
  from: oldPkgLink(pkg),
  to: pkgLink(pkg),
  status: 301,
})))
