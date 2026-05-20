import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/custom-component/de-tabs/types', () => ({}))

vi.mock('@/utils/generateID', () => ({
  default: () => 'generated-id-123'
}))

import DeFullTabs from '../DeFullTabs.vue'

const mountComponent = (props = {}) =>
  shallowMount(DeFullTabs, {
    props: {
      addable: false,
      ...props
    },
    global: {
      stubs: {
        'el-tabs': { template: '<div class="el-tabs"><slot /><slot name="add" /></div>' },
        'el-tab-pane': { template: '<div class="el-tab-pane"><slot /><slot name="label" /></div>' },
        'el-button': { template: '<button><slot /></button>' },
        'el-icon': { template: '<i><slot /></i>' },
        'el-dropdown': {
          template: '<div class="el-dropdown"><slot /><slot name="dropdown" /></div>'
        },
        'el-dropdown-menu': { template: '<div><slot /></div>' },
        'el-dropdown-item': { template: '<div><slot /></div>' }
      }
    }
  })

describe('de-screen/DeFullTabs', () => {
  it('renders the root container', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('.fu-tabs').exists()).toBe(true)
  })

  it('accepts addable prop default false', () => {
    const wrapper = mountComponent()
    expect(wrapper.props('addable')).toBe(false)
  })

  it('accepts addable prop true', () => {
    const wrapper = mountComponent({ addable: true })
    expect(wrapper.props('addable')).toBe(true)
  })

  it('accepts addType prop with default', () => {
    const wrapper = mountComponent()
    expect(wrapper.props('addType')).toBe('default')
  })

  it('accepts dropdownMenus prop', () => {
    const menus = [{ label: 'Item 1', command: 'cmd1' }]
    const wrapper = mountComponent({ dropdownMenus: menus })
    expect(wrapper.props('dropdownMenus')).toEqual(menus)
  })

  it('emits command event via handleCommand', async () => {
    const wrapper = mountComponent({ addable: true })
    const vm = wrapper.vm as any
    vm.handleCommand('test-cmd')
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('command')).toBeTruthy()
    const emittedArgs = wrapper.emitted('command')![0]
    expect(emittedArgs[0]).toBe('generated-id-123')
  })

  it('accepts addIcon prop with default Plus', () => {
    const wrapper = mountComponent()
    expect(wrapper.props('addIcon')).toBe('Plus')
  })
})
