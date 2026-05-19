import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => key
  })
}))

import ScrollShadow from '../ScrollShadow.vue'

describe('ScrollShadow', () => {
  it('renders the scroll shadow content div', () => {
    const wrapper = shallowMount(ScrollShadow)

    expect(wrapper.find('.scroll-shadow-content').exists()).toBe(true)
  })

  it('contains the placeholder text tet', () => {
    const wrapper = shallowMount(ScrollShadow)

    expect(wrapper.text()).toContain('tet')
  })

  it('applies the scroll-shadow-content class', () => {
    const wrapper = shallowMount(ScrollShadow)

    expect(wrapper.classes()).toContain('scroll-shadow-content')
  })
})
