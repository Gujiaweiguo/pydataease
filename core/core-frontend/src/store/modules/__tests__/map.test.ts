import { beforeEach, describe, expect, it } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

import { useMapStore } from '../map'

describe('useMapStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('has the expected initial state', () => {
    const store = useMapStore()

    expect(store.mapCache).toEqual({})
    expect(store.mapKey).toEqual({
      key: '',
      securityCode: '',
      mapType: ''
    })
  })

  it('stores map geoJson by id', () => {
    const store = useMapStore()
    const geoJson = { type: 'FeatureCollection', features: [] }

    store.setMap({ id: 'china', geoJson })

    expect(store.mapCache.china).toEqual(geoJson)
  })

  it('keeps multiple cached maps', () => {
    const store = useMapStore()

    store.setMap({ id: 'china', geoJson: { type: 'FeatureCollection', features: [] } })
    store.setMap({ id: 'world', geoJson: { type: 'FeatureCollection', features: [{ id: 1 }] } })

    expect(Object.keys(store.mapCache)).toEqual(['china', 'world'])
    expect(store.mapCache.world.features).toEqual([{ id: 1 }])
  })

  it('overwrites an existing cached map when the id matches', () => {
    const store = useMapStore()

    store.setMap({ id: 'china', geoJson: { type: 'FeatureCollection', features: [{ id: 1 }] } })
    store.setMap({ id: 'china', geoJson: { type: 'FeatureCollection', features: [{ id: 2 }] } })

    expect(store.mapCache.china.features).toEqual([{ id: 2 }])
  })

  it('replaces the map key metadata without touching the cache', () => {
    const store = useMapStore()
    store.setMap({ id: 'china', geoJson: { type: 'FeatureCollection', features: [] } })

    store.setKey({ key: 'ak', securityCode: 'secret', mapType: 'gaode' })

    expect(store.mapKey).toEqual({ key: 'ak', securityCode: 'secret', mapType: 'gaode' })
    expect(store.mapCache.china).toBeDefined()
  })
})
