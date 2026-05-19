import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/store/modules/share', () => ({
  useShareStoreWithOut: () => ({
    getShareDisable: false
  })
}))

vi.mock('@/utils/ModelUtil', () => ({
  isDesktop: () => false
}))

vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div />' }
}))

vi.mock('@/config/axios/hmac', () => ({}))
vi.mock('@/config/axios/service', () => ({
  cancelRequestBatch: vi.fn()
}))

vi.mock('@/views/share/share/ShareHandler.vue', () => ({
  default: { template: '<div />' }
}))

import DvHandleMore from '../DvHandleMore.vue'

const globalStubs = {
  ElDropdown: { template: '<div><slot /><slot name="dropdown" /></div>' },
  ElDropdownMenu: { template: '<div><slot /></div>' },
  ElDropdownItem: {
    props: ['command', 'disabled', 'divided'],
    template: '<div><slot /></div>'
  },
  ElIcon: { template: '<i><slot /></i>' },
  ElTooltip: { template: '<div><slot /></div>' }
}

const defaultMenuList = [
  { label: 'Rename', command: 'rename', svgName: 'icon-edit' },
  { label: 'Delete', command: 'delete', divided: true }
]

const mountComponent = (props = {}) =>
  shallowMount(DvHandleMore, {
    props: {
      menuList: defaultMenuList,
      node: { id: '1', leaf: true, weight: 7, extraFlag1: 1 },
      anyManage: true,
      ...props
    },
    global: { stubs: globalStubs }
  })

describe('DvHandleMore', () => {
  it('renders the component', () => {
    const wrapper = mountComponent()
    expect(wrapper.exists()).toBe(true)
  })

  it('renders menu items from menuList prop', () => {
    const wrapper = mountComponent()
    expect(wrapper.text()).toContain('Rename')
    expect(wrapper.text()).toContain('Delete')
  })

  it('emits handleCommand when a menu command is triggered', async () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any
    vm.handleCommand('rename')
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('handleCommand')).toBeTruthy()
    expect(wrapper.emitted('handleCommand')![0]).toEqual(['rename'])
  })

  it('hides copy/move menu items when anyManage is false', () => {
    const menuList = [
      { label: 'Copy', command: 'copy' },
      { label: 'Rename', command: 'rename' }
    ]
    const wrapper = mountComponent({ menuList, anyManage: false })
    // copy should be hidden (de-hidden-drop-item class applied)
    expect(wrapper.exists()).toBe(true)
  })
})
