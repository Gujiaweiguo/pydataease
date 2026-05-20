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
    dvInfo: { value: { type: 'dashboard' } },
    mobileInPc: { value: false }
  })
}))
vi.mock('pinia', () => ({
  storeToRefs: (store: any) => store
}))

import DragInfo from '../DragInfo.vue'

describe('DragInfo', () => {
  it('renders component', () => {
    const wrapper = shallowMount(DragInfo, {
      global: {
        stubs: {
          'el-row': { template: '<div><slot /></div>' },
          Icon: { template: '<div><slot /></div>' },
          'dv-drag-tips': true
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains drag-info-main wrapper', () => {
    const wrapper = shallowMount(DragInfo, {
      global: {
        stubs: {
          'el-row': { template: '<div><slot /></div>' },
          Icon: { template: '<div><slot /></div>' },
          'dv-drag-tips': true
        }
      }
    })
    expect(wrapper.find('.drag-info-main').exists()).toBe(true)
  })
})
