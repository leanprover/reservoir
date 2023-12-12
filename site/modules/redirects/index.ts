import { defineRedirectsModule } from './module'
import { type Package, packages } from '../../utils/manifest'
import pkgLink from '../../utils/pkgLink'

const oldPkgLink = (pkg: Package) => {
  const id = pkg['fullName'].replace('-', '--').replace('/', '-')
  return `/packages/${encodeURIComponent(id)}`
}

export default defineRedirectsModule(packages.map(pkg => ({
  from: oldPkgLink(pkg),
  to: pkgLink(pkg),
  status: 301,
})))
