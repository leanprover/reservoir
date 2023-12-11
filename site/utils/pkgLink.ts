export default function pkgLink(pkg: Package) {
  return `/@${encodeURIComponent(pkg.owner)}/${encodeURIComponent(pkg.name)}`
}
