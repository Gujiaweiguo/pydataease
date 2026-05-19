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
vi.mock('@/assets/svg/dv-richText.svg', () => ({ default: 'richtext' }))
vi.mock('@/assets/svg/dv-scroll-text.svg', () => ({ default: 'scrolltext' }))

import TextGroup from '../TextGroup.vue'

const globalStubs = {
  DragComponent: {
    template: '<div class="drag-stub" @click="$emit(\'click\')"><slot /></div>',
    props: ['themes', 'icon', 'label', 'dragInfo']
  }
}

describe('TextGroup', () => {
  it('renders with default dataV dvModel', () => {
    const wrapper = shallowMount(TextGroup, { global: { stubs: globalStubs } })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.group').exists()).toBe(true)
  })

  it('shows scroll text component when dvModel is dataV', () => {
    const wrapper = shallowMount(TextGroup, {
      props: { dvModel: 'dataV' },
      global: { stubs: globalStubs }
    })
    const dragComponents = wrapper.findAll('.drag-stub')
    expect(dragComponents.length).toBe(2)
  })

  it('hides scroll text component when dvModel is dv', () => {
    const wrapper = shallowMount(TextGroup, {
      props: { dvModel: 'dv' },
      global: { stubs: globalStubs }
    })
    const dragComponents = wrapper.findAll('.drag-stub')
    expect(dragComponents.length).toBe(1)
  })

  it('passes themes to drag components', () => {
    const wrapper = shallowMount(TextGroup, {
      props: { themes: 'light' },
      global: { stubs: globalStubs }
    })
    const dc = wrapper.find('.drag-stub')
    expect(dc.exists()).toBe(true)
  })
})
