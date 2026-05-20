import { describe, it, expect, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (k: string) => k
  })
}))
vi.mock('@/utils/propTypes', () => ({
  propTypes: {
    arrayOf: vi.fn(() => ({
      def: vi.fn((v: any) => v)
    })),
    string: {
      def: vi.fn((v: string) => v)
    },
    shape: vi.fn(() => ({}))
  }
}))
vi.mock('@/components/drawer-filter/src/DrawerFilter.vue', () => ({
  default: { name: 'DrawerFilter', template: '<div />' }
}))
vi.mock('@/components/drawer-filter/src/DrawerEnumFilter.vue', () => ({
  default: { name: 'DrawerEnumFilter', template: '<div />' }
}))
vi.mock('@/components/drawer-filter/src/DrawerTimeFilter.vue', () => ({
  default: { name: 'DrawerTimeFilter', template: '<div />' }
}))
vi.mock('@/components/drawer-filter/src/DrawerTreeFilter.vue', () => ({
  default: { name: 'DrawerTreeFilter', template: '<div />' }
}))

import DrawerMain from '../DrawerMain.vue'

describe('DrawerMain', () => {
  it('should import DrawerMain successfully', () => {
    expect(DrawerMain).toBeDefined()
  })

  it('should be a valid Vue component', () => {
    expect(typeof DrawerMain).toBe('object')
    expect(DrawerMain.setup || DrawerMain.render || DrawerMain.__name).toBeDefined()
  })
})
