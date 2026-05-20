import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import Component from '../Component.vue'

describe('group-area Component', () => {
  it('renders successfully with area div', () => {
    const wrapper = mount(Component)
    expect(wrapper.find('.area').exists()).toBe(true)
  })

  it('area div is the root element', () => {
    const wrapper = mount(Component)
    expect(wrapper.element.tagName).toBe('DIV')
    expect(wrapper.classes()).toContain('area')
  })
})
