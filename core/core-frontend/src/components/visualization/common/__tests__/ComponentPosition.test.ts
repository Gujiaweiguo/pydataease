import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    curComponent: {
      value: {
        style: { width: 100, height: 100, top: 0, left: 0 },
        component: 'UserView',
        isLock: false,
        maintainRadio: false,
        canvasId: 'canvas-main'
      }
    },
    canvasStyleData: { value: { scale: 100 } }
  })
}))
vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: vi.fn()
  })
}))
vi.mock('@/utils/attr', () => ({
  positionData: [
    { key: 'width', label: 'W', min: 0, max: 9999, step: 1 },
    { key: 'height', label: 'H', min: 0, max: 9999, step: 1 },
    { key: 'top', label: 'Y', min: 0, max: 9999, step: 1 },
    { key: 'left', label: 'X', min: 0, max: 9999, step: 1 }
  ]
}))
vi.mock('@/utils/style', () => ({
  groupSizeStyleAdaptor: vi.fn(),
  groupStyleRevert: vi.fn()
}))
vi.mock('@/utils/canvasUtils', () => ({
  isGroupCanvas: vi.fn(() => false),
  isTabCanvas: vi.fn(() => false)
}))
vi.mock('pinia', () => ({
  storeToRefs: (store: any) => store
}))
vi.mock('lodash', () => ({ default: { forEach: vi.fn() } }))

import ComponentPosition from '../ComponentPosition.vue'

describe('ComponentPosition', () => {
  it('renders component', () => {
    const wrapper = shallowMount(ComponentPosition, {
      props: { themes: 'dark' },
      global: {
        stubs: {
          'el-form': { template: '<div><slot /></div>' },
          'el-row': { template: '<div><slot /></div>' },
          'el-col': { template: '<div><slot /></div>' },
          'el-form-item': { template: '<div><slot /></div>' },
          'el-input-number': true,
          'el-checkbox': true
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
