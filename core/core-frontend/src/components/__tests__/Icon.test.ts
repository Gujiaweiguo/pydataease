import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import Icon from '../icon-custom/src/Icon.vue'

describe('Icon', () => {
  it('renders slot content when staticContent is not provided', () => {
    const wrapper = mount(Icon, {
      slots: {
        default: '<svg class="slot-icon"></svg>'
      }
    })

    expect(wrapper.find('.slot-icon').exists()).toBe(true)
    expect(wrapper.find('.svg-container').exists()).toBe(false)
  })

  it('renders static content inside the svg container', () => {
    const wrapper = mount(Icon, {
      props: {
        staticContent: '<svg class="static-icon"></svg>'
      }
    })

    expect(wrapper.find('.svg-container').exists()).toBe(true)
    expect(wrapper.html()).toContain('static-icon')
  })

  it('applies the computed svg classes to the static content container', () => {
    const wrapper = mount(Icon, {
      props: {
        staticContent: '<svg></svg>',
        className: 'custom-icon'
      }
    })

    expect(wrapper.find('.svg-container').classes()).toEqual(
      expect.arrayContaining(['svg-container', 'svg-icon', 'custom-icon'])
    )
  })
})
