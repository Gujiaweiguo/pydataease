import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/components/icon-custom/src/Icon.vue', () => ({
  default: { template: '<span><slot /></span>' }
}))

import DragComponent from '../DragComponent.vue'

describe('DragComponent', () => {
  it('renders with required label and dragInfo props', () => {
    const wrapper = shallowMount(DragComponent, {
      props: { label: 'Picture', dragInfo: 'Picture&Picture' },
      global: { stubs: {} }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.text()).toContain('Picture')
  })

  it('applies dark theme class by default', () => {
    const wrapper = shallowMount(DragComponent, {
      props: { label: 'Test', dragInfo: 'Test&Test' },
      global: { stubs: {} }
    })
    expect(wrapper.find('.drag-dark').exists()).toBe(true)
  })

  it('applies light theme class when themes is light', () => {
    const wrapper = shallowMount(DragComponent, {
      props: { label: 'Test', dragInfo: 'Test&Test', themes: 'light' },
      global: { stubs: {} }
    })
    expect(wrapper.find('.drag-light').exists()).toBe(true)
  })

  it('renders draggable area with data-id attribute', () => {
    const wrapper = shallowMount(DragComponent, {
      props: { label: 'Video', dragInfo: 'DeVideo&DeVideo' },
      global: { stubs: {} }
    })
    const dragArea = wrapper.find('.icon-content')
    expect(dragArea.exists()).toBe(true)
    expect(dragArea.attributes('data-id')).toBe('DeVideo&DeVideo')
    expect(dragArea.attributes('draggable')).toBe('true')
  })

  it('renders name span when name prop is provided', () => {
    const wrapper = shallowMount(DragComponent, {
      props: { label: 'Test', dragInfo: 'Test&Test', name: 'CustomName' },
      global: { stubs: {} }
    })
    const nameSpan = wrapper.findAll('.label-content')
    const hasCustomName = nameSpan.some(el => el.text().includes('CustomName'))
    expect(hasCustomName).toBe(true)
  })
})
