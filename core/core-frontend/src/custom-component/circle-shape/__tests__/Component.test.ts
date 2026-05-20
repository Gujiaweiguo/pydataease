import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

import Component from '../Component.vue'

describe('circle-shape/Component.vue', () => {
  it('renders the component', () => {
    const wrapper = shallowMount(Component, {
      props: {
        propValue: 'test',
        element: { propValue: null }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the circle-shape container', () => {
    const wrapper = shallowMount(Component, {
      props: {
        propValue: 'test',
        element: { propValue: null }
      }
    })
    expect(wrapper.find('.circle-shape').exists()).toBe(true)
  })

  it('accepts propValue string', () => {
    const wrapper = shallowMount(Component, {
      props: {
        propValue: 'hello world',
        element: { propValue: null }
      }
    })
    expect(wrapper.props('propValue')).toBe('hello world')
  })

  it('uses default element when not provided', () => {
    const wrapper = shallowMount(Component, {
      props: { propValue: 'test' }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
