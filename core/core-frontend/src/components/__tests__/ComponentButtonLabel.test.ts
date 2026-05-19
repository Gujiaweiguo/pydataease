import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import ComponentButtonLabel from '../visualization/ComponentButtonLabel.vue'

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

const ElDividerStub = defineComponent({
  name: 'ElDivider',
  template: '<div class="el-divider-stub"></div>'
})

describe('ComponentButtonLabel', () => {
  it('renders the title and icon content', () => {
    const wrapper = mount(ComponentButtonLabel, {
      props: {
        title: 'Layout',
        iconName: DummyIcon
      },
      global: {
        stubs: {
          ElRow: ElRowStub,
          ElCol: ElColStub,
          ElDivider: ElDividerStub
        }
      }
    })

    expect(wrapper.text()).toContain('Layout')
    expect(wrapper.find('.dummy-icon').exists()).toBe(true)
  })

  it('renders a divider only when showSplitLine is enabled', () => {
    const withDivider = mount(ComponentButtonLabel, {
      props: {
        showSplitLine: true,
        iconName: DummyIcon
      },
      global: {
        stubs: {
          ElRow: ElRowStub,
          ElCol: ElColStub,
          ElDivider: ElDividerStub
        }
      }
    })

    const withoutDivider = mount(ComponentButtonLabel, {
      props: {
        showSplitLine: false,
        iconName: DummyIcon
      },
      global: {
        stubs: {
          ElRow: ElRowStub,
          ElCol: ElColStub,
          ElDivider: ElDividerStub
        }
      }
    })

    expect(withDivider.find('.el-divider-stub').exists()).toBe(true)
    expect(withoutDivider.find('.el-divider-stub').exists()).toBe(false)
  })

  it('applies the active class when active is true', () => {
    const wrapper = mount(ComponentButtonLabel, {
      props: {
        active: true,
        iconName: DummyIcon
      },
      global: {
        stubs: {
          ElRow: ElRowStub,
          ElCol: ElColStub,
          ElDivider: ElDividerStub
        }
      }
    })

    expect(wrapper.find('.group_inner').classes()).toContain('inner-active')
  })

  it('emits customClick when the row is clicked', async () => {
    const wrapper = mount(ComponentButtonLabel, {
      props: {
        iconName: DummyIcon
      },
      global: {
        stubs: {
          ElRow: ElRowStub,
          ElCol: ElColStub,
          ElDivider: ElDividerStub
        }
      }
    })

    await wrapper.find('.group_icon').trigger('click')

    expect(wrapper.emitted('customClick')).toHaveLength(1)
  })
})
