import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

const storeState = vi.hoisted(() => ({
  canvasStyleData: {
    component: {
      seniorStyleSetting: {
        drillLayerColor: '#123456'
      }
    }
  }
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => key
  })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => storeState
}))

import DrillPath from '../DrillPath.vue'

const globalStubs = {
  ElBreadcrumb: {
    props: ['separatorIcon'],
    template: '<div class="breadcrumb-stub"><slot /></div>'
  },
  ElBreadcrumbItem: {
    emits: ['click'],
    template: '<div class="breadcrumb-item-stub" @click="$emit(\'click\')"><slot /></div>'
  }
}

const mountComponent = (props: Record<string, unknown> = {}) =>
  shallowMount(DrillPath, {
    props,
    global: {
      stubs: globalStubs
    }
  })

describe('DrillPath', () => {
  it('does not render when there are no drill filters', () => {
    const wrapper = mountComponent({ drillFilters: [] })

    expect(wrapper.find('.drill').exists()).toBe(false)
  })

  it('renders drill entries and emits jumps for breadcrumb clicks', async () => {
    const wrapper = mountComponent({
      drillFilters: [{ value: ['North'] }, { value: ['Beijing'] }]
    })

    const items = wrapper.findAll('.breadcrumb-item-stub')
    await items[0].trigger('click')
    await items[1].trigger('click')

    expect(wrapper.text()).toContain('commons.all')
    expect(wrapper.text()).toContain('North')
    expect(wrapper.emitted('onDrillJump')).toEqual([[0], [1]])
  })

  it('ignores jumps beyond the current drill depth', () => {
    const wrapper = mountComponent({
      drillFilters: [{ value: ['North'] }]
    })

    ;(wrapper.vm as any).drillJump(3)

    expect(wrapper.emitted('onDrillJump')).toBeUndefined()
  })

  it('applies disabled styling and exposes the store-driven drill color variable', () => {
    const wrapper = mountComponent({
      drillFilters: [{ value: ['North'] }],
      disabled: true
    })

    expect(wrapper.get('.drill').classes()).toContain('noClick')
    expect(wrapper.get('.drill').attributes('style')).toContain('--drill-color: #123456;')
  })
})
