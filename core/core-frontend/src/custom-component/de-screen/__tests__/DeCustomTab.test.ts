import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import DeCustomTab from '../DeCustomTab.vue'

const mountComponent = (props = {}) =>
  shallowMount(DeCustomTab, {
    props: {
      fontColor: 'red',
      activeColor: 'blue',
      borderColor: 'green',
      borderActiveColor: 'yellow',
      hideTitle: false,
      ...props
    },
    global: {
      stubs: {
        'el-tabs': { template: '<div class="el-tabs"><slot /></div>' }
      }
    }
  })

describe('de-screen/DeCustomTab', () => {
  it('renders the root container', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('.de-tabs').exists()).toBe(true)
  })

  it('accepts fontColor prop', () => {
    const wrapper = mountComponent({ fontColor: '#333' })
    expect(wrapper.props('fontColor')).toBe('#333')
  })

  it('accepts activeColor prop', () => {
    const wrapper = mountComponent({ activeColor: '#fff' })
    expect(wrapper.props('activeColor')).toBe('#fff')
  })

  it('accepts hideTitle prop', () => {
    const wrapper = mountComponent({ hideTitle: true })
    expect(wrapper.props('hideTitle')).toBe(true)
  })

  it('accepts styleType prop with default empty string', () => {
    const wrapper = mountComponent()
    expect(wrapper.props('styleType')).toBe('')
  })

  it('applies no-header class when hideTitle is true', () => {
    const wrapper = mountComponent({ hideTitle: true })
    expect(wrapper.find('.no-header').exists()).toBe(true)
  })

  it('applies noBorder class when borderColor is none', () => {
    const wrapper = mountComponent({ borderColor: 'none' })
    expect(wrapper.find('.noBorder').exists()).toBe(true)
  })
})
