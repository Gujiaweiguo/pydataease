import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import ComponentButton from '../visualization/ComponentButton.vue'

const DummyIcon = defineComponent({
  name: 'DummyIcon',
  template: '<svg class="dummy-icon"></svg>'
})

const ElRowStub = defineComponent({
  name: 'ElRow',
  template: '<div class="el-row-stub"><slot /></div>'
})

const ElColStub = defineComponent({
  name: 'ElCol',
  template: '<div class="el-col-stub"><slot /></div>'
})

describe('ComponentButton', () => {
  it('renders the title, tooltip and icon', () => {
    const wrapper = mount(ComponentButton, {
      props: {
        title: 'Preview',
        tips: 'Open preview mode',
        iconName: DummyIcon
      },
      global: {
        stubs: {
          ElRow: ElRowStub,
          ElCol: ElColStub
        }
      }
    })

    expect(wrapper.find('.group_icon').attributes('title')).toBe('Open preview mode')
    expect(wrapper.text()).toContain('Preview')
    expect(wrapper.find('.dummy-icon').exists()).toBe(true)
  })

  it('applies active and split line classes from props', () => {
    const wrapper = mount(ComponentButton, {
      props: {
        active: true,
        showSplitLine: true,
        iconName: DummyIcon
      },
      global: {
        stubs: {
          ElRow: ElRowStub,
          ElCol: ElColStub
        }
      }
    })

    expect(wrapper.find('.group_icon').classes()).toContain('group-right-border')
    expect(wrapper.find('.group_inner').classes()).toContain('inner-active')
  })

  it('emits customClick when the button row is clicked', async () => {
    const wrapper = mount(ComponentButton, {
      props: {
        iconName: DummyIcon
      },
      global: {
        stubs: {
          ElRow: ElRowStub,
          ElCol: ElColStub
        }
      }
    })

    await wrapper.find('.group_icon').trigger('click')

    expect(wrapper.emitted('customClick')).toHaveLength(1)
  })
})
