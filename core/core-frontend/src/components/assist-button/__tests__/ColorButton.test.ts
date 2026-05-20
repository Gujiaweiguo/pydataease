import { describe, it, expect } from 'vitest'
import { shallowMount } from '@vue/test-utils'

import ColorButton from '../ColorButton.vue'

describe('ColorButton', () => {
  it('should render without errors', () => {
    const wrapper = shallowMount(ColorButton, {
      props: { colorType: 'light', label: 'light' }
    })
    expect(wrapper.find('.color-button-main').exists()).toBe(true)
  })

  it('should show active state when label matches colorType', () => {
    const wrapper = shallowMount(ColorButton, {
      props: { colorType: 'light', label: 'light' }
    })
    expect(wrapper.find('.color-button-active').exists()).toBe(true)
  })

  it('should not show active state when label differs from colorType', () => {
    const wrapper = shallowMount(ColorButton, {
      props: { colorType: 'light', label: 'dark' }
    })
    expect(wrapper.find('.color-button-active').exists()).toBe(false)
  })

  it('should emit onClick with colorType when clicked', async () => {
    const wrapper = shallowMount(ColorButton, {
      props: { colorType: 'dark', label: 'light' }
    })
    const outer = wrapper.find('.color-button-outer')
    await outer.trigger('click')
    expect(wrapper.emitted('onClick')).toBeTruthy()
    expect(wrapper.emitted('onClick')![0]).toEqual(['dark'])
  })

  it('should render slot content', () => {
    const wrapper = shallowMount(ColorButton, {
      props: { colorType: 'light' },
      slots: {
        default: '<span class="btn-label">Light</span>'
      }
    })
    expect(wrapper.find('.btn-label').exists()).toBe(true)
  })
})
