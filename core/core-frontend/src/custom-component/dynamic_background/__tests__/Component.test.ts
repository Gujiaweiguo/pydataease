import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

import Component from '../Component.vue'

describe('dynamic_background/Component.vue', () => {
  it('renders the component', () => {
    const wrapper = shallowMount(Component, {
      props: {
        element: { innerType: 'test-bg.png' }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the circle-shape container', () => {
    const wrapper = shallowMount(Component, {
      props: {
        element: { innerType: 'test-bg.png' }
      }
    })
    expect(wrapper.find('.circle-shape').exists()).toBe(true)
  })

  it('renders an img element', () => {
    const wrapper = shallowMount(Component, {
      props: {
        element: { innerType: 'test-bg.png' }
      }
    })
    expect(wrapper.find('img').exists()).toBe(true)
  })

  it('uses default element prop when not provided', () => {
    const wrapper = shallowMount(Component)
    expect(wrapper.exists()).toBe(true)
  })
})
