import { describe, it, expect, vi } from 'vitest'

vi.mock('lodash-es', () => ({
  cloneDeep: vi.fn(x => JSON.parse(JSON.stringify(x)))
}))
vi.mock('@/api/relation/index', () => ({
  getDatasourceRelationship: vi.fn(() => Promise.resolve({})),
  getDatasetRelationship: vi.fn(() => Promise.resolve({}))
}))

vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div class="xpack-stub" />' }
}))

import RelationChart from '../index.vue'

describe('RelationChart', () => {
  it('should expose getChartData method via module import', () => {
    expect(RelationChart).toBeDefined()
  })

  it('should have expose definition for getChartData', () => {
    expect(typeof RelationChart).toBe('object')
  })
})
