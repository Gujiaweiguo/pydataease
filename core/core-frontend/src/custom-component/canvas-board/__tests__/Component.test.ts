import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/components/de-board/Board.vue', () => ({
  default: { template: '<div class="board-stub"></div>' }
}))

import Component from '../Component.vue'

describe('canvas-board/Component.vue', () => {
  it('renders the component', () => {
    const wrapper = shallowMount(Component, {
      props: {
        propValue: 'test',
        element: { innerType: 'DeBoard1' }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('passes innerType to Board component', () => {
    const wrapper = shallowMount(Component, {
      props: {
        propValue: 'test',
        element: { innerType: 'DeBoard5' }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('uses default element when innerType is null', () => {
    const wrapper = shallowMount(Component, {
      props: {
        propValue: 'test'
      }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
