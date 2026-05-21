interface AreaNode {
  id: string
  name: string
  level: string
  pid: string
  children: AreaNode[]
}

interface CustomGeoArea {
  id: string
  name: string
  disabled?: boolean
  children?: CustomGeoArea[]
}

type CustomGeoSubArea = CustomGeoArea & {
  geoAreaId: string
  scope: string
  scopeArr?: string[]
  centroid?: [number, number]
}
