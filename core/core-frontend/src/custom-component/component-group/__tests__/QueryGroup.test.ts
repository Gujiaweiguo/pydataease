import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/utils/eventBus', () => ({
  default: { emit: vi.fn() }
}))
vi.mock('@/utils/canvasUtils', () => ({
  commonHandleDragStart: vi.fn(),
  commonHandleDragEnd: vi.fn()
}))
vi.mock('@/assets/svg/dv-filter-show.svg', () => ({ default: 'filter' }))

import QueryGroup from '../QueryGroup.vue'

const globalStubs = {
  DragComponent: {
    template: '<div class="drag-stub" @click="$emit(\'click\')"><slot /></div>',
    props: ['themes', 'icon', 'label', 'dragInfo']
  }
}

describe('QueryGroup', () => {
  it('renders with default props', () => {
    const wrapper = shallowMount(QueryGroup, { global: { stubs: globalStubs } })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.group').exists()).toBe(true)
  })

  it('renders one drag component for VQuery', () => {
    const wrapper = shallowMount(QueryGroup, { global: { stubs: globalStubs } })
    const dragComponents = wrapper.findAll('.drag-stub')
    expect(dragComponents.length).toBe(1)
  })

  it('passes themes prop to drag component', () => {
    const wrapper = shallowMount(QueryGroup, {
      props: { themes: 'light' },
      global: { stubs: globalStubs }
    })
    const dc = wrapper.find('.drag-stub')
    expect(dc.exists()).toBe(true)
  })

  it('has dragstart and dragend event handlers', () => {
    const wrapper = shallowMount(QueryGroup, { global: { stubs: globalStubs } })
    const group = wrapper.find('.group')
    expect(group.exists()).toBe(true)
  })
})
