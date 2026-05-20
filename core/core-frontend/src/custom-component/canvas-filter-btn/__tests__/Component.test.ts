import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import { ref } from 'vue'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    canvasState: { curPointArea: 'base' },
    popAreaActiveSwitch: vi.fn()
  })
}))
vi.mock('pinia', async importOriginal => {
  const actual = (await importOriginal()) as any
  return {
    ...actual,
    storeToRefs: () => ({
      canvasState: ref({ curPointArea: 'base' })
    })
  }
})

import Component from '../Component.vue'

describe('canvas-filter-btn Component', () => {
  it('renders successfully with canvas-filter class', () => {
    const wrapper = shallowMount(Component, {
      props: { isFixed: false },
      global: {
        stubs: {
          ElTooltip: { template: '<div class="el-tooltip-stub"><slot /></div>' },
          ElIcon: { template: '<div class="el-icon-stub"><slot /></div>' },
          Filter: { template: '<span class="filter-icon">filter</span>' }
        }
      }
    })
    expect(wrapper.find('.canvas-filter').exists()).toBe(true)
  })

  it('applies filter-btn-fix class when isFixed is true', () => {
    const wrapper = shallowMount(Component, {
      props: { isFixed: true },
      global: {
        stubs: {
          ElTooltip: { template: '<div><slot /></div>' },
          ElIcon: { template: '<div><slot /></div>' },
          Filter: { template: '<span>filter</span>' }
        }
      }
    })
    expect(wrapper.find('.filter-btn-fix').exists()).toBe(true)
  })

  it('does not apply filter-btn-fix class when isFixed is false', () => {
    const wrapper = shallowMount(Component, {
      props: { isFixed: false },
      global: {
        stubs: {
          ElTooltip: { template: '<div><slot /></div>' },
          ElIcon: { template: '<div><slot /></div>' },
          Filter: { template: '<span>filter</span>' }
        }
      }
    })
    expect(wrapper.find('.filter-btn-fix').exists()).toBe(false)
  })
})
