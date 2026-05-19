import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))

import DragPlaceholder from '../DragPlaceholder.vue'

describe('DragPlaceholder', () => {
  it('renders placeholder when dragList is empty', () => {
    const wrapper = shallowMount(DragPlaceholder, {
      props: { dragList: [], themes: 'dark' }
    })
    expect(wrapper.find('.drag-placeholder-style').exists()).toBe(true)
    expect(wrapper.text()).toContain('chart.placeholder_field')
  })

  it('does not render placeholder when dragList has items', () => {
    const wrapper = shallowMount(DragPlaceholder, {
      props: { dragList: [{ id: '1', name: 'field' }], themes: 'dark' }
    })
    expect(wrapper.find('.drag-placeholder-style').exists()).toBe(false)
  })

  it('renders placeholder when dragList is undefined', () => {
    const wrapper = shallowMount(DragPlaceholder, {
      props: { dragList: undefined as any, themes: 'dark' }
    })
    expect(wrapper.find('.drag-placeholder-style').exists()).toBe(true)
  })

  it('applies dark theme class when themes is dark', () => {
    const wrapper = shallowMount(DragPlaceholder, {
      props: { dragList: [], themes: 'dark' }
    })
    expect(wrapper.find('.drag-placeholder-style-span--dark').exists()).toBe(true)
  })

  it('does not apply dark class when themes is light', () => {
    const wrapper = shallowMount(DragPlaceholder, {
      props: { dragList: [], themes: 'light' }
    })
    expect(wrapper.find('.drag-placeholder-style-span--dark').exists()).toBe(false)
  })

  it('applies marginTop style from prop', () => {
    const wrapper = shallowMount(DragPlaceholder, {
      props: { dragList: [], themes: 'dark', marginTop: '10px' }
    })
    const el = wrapper.find('.drag-placeholder-style')
    expect(el.exists()).toBe(true)
  })
})
