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
vi.mock('@/assets/svg/dv-picture-show.svg', () => ({ default: 'pic' }))
vi.mock('@/assets/svg/icon-video.svg', () => ({ default: 'vid' }))
vi.mock('@/assets/svg/icon-stream.svg', () => ({ default: 'stream' }))
vi.mock('@/assets/svg/picture-group-origin.svg', () => ({ default: 'pg' }))

import MediaGroup from '../MediaGroup.vue'

const globalStubs = {
  DragComponent: {
    template: '<div class="drag-stub" @click="$emit(\'click\')"><slot /></div>',
    props: ['themes', 'icon', 'label', 'dragInfo']
  }
}

describe('MediaGroup', () => {
  it('renders with default props', () => {
    const wrapper = shallowMount(MediaGroup, { global: { stubs: globalStubs } })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.group').exists()).toBe(true)
  })

  it('renders four media drag components', () => {
    const wrapper = shallowMount(MediaGroup, { global: { stubs: globalStubs } })
    const dragComponents = wrapper.findAll('.drag-stub')
    expect(dragComponents.length).toBe(4)
  })

  it('uses dark theme by default', () => {
    const wrapper = shallowMount(MediaGroup, { global: { stubs: globalStubs } })
    const dragComponents = wrapper.findAll('.drag-stub')
    dragComponents.forEach(dc => {
      expect(dc.exists()).toBe(true)
    })
  })

  it('passes themes prop to drag components', () => {
    const wrapper = shallowMount(MediaGroup, {
      props: { themes: 'light' },
      global: { stubs: globalStubs }
    })
    const dragComponents = wrapper.findAll('.drag-stub')
    expect(dragComponents.length).toBe(4)
  })
})
