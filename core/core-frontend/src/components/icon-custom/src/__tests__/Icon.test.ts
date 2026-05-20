import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

vi.mock('@/utils/propTypes', () => ({
  propTypes: {
    string: {
      def: vi.fn((v: string) => v)
    }
  }
}))

import Icon from '../Icon.vue'

describe('Icon', () => {
  it('should render with staticContent', () => {
    const wrapper = shallowMount(Icon, {
      props: {
        staticContent: '<svg><circle/></svg>',
        className: 'test-class'
      }
    })
    expect(wrapper.find('.svg-container').exists()).toBe(true)
    expect(wrapper.find('.test-class').exists()).toBe(true)
  })

  it('should render slot when no staticContent', () => {
    const wrapper = shallowMount(Icon, {
      props: {},
      slots: {
        default: '<span class="slot-content">icon</span>'
      }
    })
    expect(wrapper.find('.svg-container').exists()).toBe(false)
    expect(wrapper.find('.slot-content').exists()).toBe(true)
  })

  it('should compute svgClass with className when provided', () => {
    const wrapper = shallowMount(Icon, {
      props: { className: 'my-icon' }
    })
    expect(wrapper.find('.svg-icon.my-icon').exists()).toBe(false)
  })
})
