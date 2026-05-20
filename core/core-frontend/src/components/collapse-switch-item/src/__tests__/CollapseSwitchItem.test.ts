import { describe, it, expect } from 'vitest'
import { shallowMount } from '@vue/test-utils'

import CollapseSwitchItem from '../CollapseSwitchItem.vue'

describe('CollapseSwitchItem', () => {
  const globalConfig = {
    global: {
      stubs: {
        'el-collapse-item': {
          template: '<div class="el-collapse-item-stub"><slot name="title" /><slot /></div>',
          props: ['effect']
        },
        'el-switch': {
          template: '<input type="checkbox" />',
          props: ['modelValue', 'effect', 'size']
        }
      }
    }
  }

  it('should render without errors', () => {
    const wrapper = shallowMount(CollapseSwitchItem, {
      props: { modelValue: true, title: 'Test Title', themes: 'dark' },
      ...globalConfig
    })
    expect(wrapper).toBeTruthy()
  })

  it('should render slot content', () => {
    const wrapper = shallowMount(CollapseSwitchItem, {
      props: { modelValue: true, title: 'Test' },
      slots: { default: '<div class="slot-content">content</div>' },
      ...globalConfig
    })
    expect(wrapper.find('.slot-content').exists()).toBe(true)
  })
})
