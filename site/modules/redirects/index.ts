import { defineRedirectsModule } from './module'
import { packages } from '../../utils/manifest'
import pkgLink from '../../utils/pkgLink'

export default defineRedirectsModule(packages.map(pkg => ({
  from: `/packages/${encodeURIComponent(pkg.id)}`,
  to: pkgLink(pkg),
  status: 301,
})))
