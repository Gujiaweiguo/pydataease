import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import ColorButton from '../assist-button/ColorButton.vue'

describe('ColorButton', () => {
  it('renders slot content', () => {
    const wrapper = mount(ColorButton, {
      props: {
        colorType: 'dark',
        label: 'light'
      },
      slots: {
        default: 'Theme option'
      }
    })

    expect(wrapper.text()).toContain('Theme option')
  })

  it('adds the active class when label matches the color type', () => {
    const wrapper = mount(ColorButton, {
      props: {
        colorType: 'dark',
        label: 'dark'
      }
    })

    expect(wrapper.find('.color-button-outer').classes()).toContain('color-button-active')
  })

  it('emits the selected color type when clicked', async () => {
    const wrapper = mount(ColorButton, {
      props: {
        colorType: 'light',
        label: 'dark'
      }
    })

    await wrapper.find('.color-button-outer').trigger('click')

    expect(wrapper.emitted('onClick')).toEqual([['light']])
  })
})
