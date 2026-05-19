import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    setCurComponent: vi.fn(),
    setEditMode: vi.fn(),
    resetDvInfo: vi.fn(),
    deleteComponentById: vi.fn(),
    updateDvInfoCall: vi.fn(),
    setClickComponentStatus: vi.fn(),
    removeViewFilter: vi.fn(),
    setLinkageTargetInfo: vi.fn(),
    curComponent: { value: null },
    componentData: { value: [] },
    dvInfo: { value: { id: 'test' } }
  })
}))

vi.mock('@/store/modules/data-visualization/copy', () => ({
  copyStoreWithOut: () => ({
    copy: vi.fn(),
    paste: vi.fn()
  })
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: vi.fn()
  })
}))

vi.mock('@/store/modules/data-visualization/layer', () => ({
  layerStoreWithOut: () => ({
    upComponent: vi.fn(),
    downComponent: vi.fn(),
    topComponent: vi.fn(),
    bottomComponent: vi.fn()
  })
}))

vi.mock('@/api/visualization/linkage', () => ({
  getViewLinkageGather: vi.fn(() => Promise.resolve({ data: {} }))
}))

vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div />' }
}))

vi.mock('@/config/axios/hmac', () => ({}))
vi.mock('@/config/axios/service', () => ({
  cancelRequestBatch: vi.fn()
}))

import SettingMenu from '../SettingMenu.vue'

const globalStubs = {
  ElDropdown: { template: '<div class="dropdown-stub"><slot /><slot name="dropdown" /></div>' },
  ElDropdownMenu: { template: '<div><slot /></div>' },
  ElDropdownItem: { template: '<div><slot /></div>' },
  ElDialog: {
    props: ['modelValue', 'visible', 'title', 'width'],
    template:
      '<div v-if="modelValue || visible" class="dialog-stub"><slot /><slot name="footer" /></div>'
  },
  ElButton: { template: '<button><slot /></button>' },
  ElIcon: { template: '<i><slot /></i>' }
}

const mountMenu = () =>
  shallowMount(SettingMenu, {
    global: { stubs: globalStubs }
  })

describe('SettingMenu', () => {
  it('renders without errors', () => {
    const wrapper = mountMenu()
    expect(wrapper.exists()).toBe(true)
  })

  it('contains a dropdown wrapper element', () => {
    const wrapper = mountMenu()
    expect(wrapper.find('.dropdown-stub').exists()).toBe(true)
  })

  it('emits boardSet event', () => {
    const wrapper = mountMenu()
    const vm = wrapper.vm as any
    vm.$emit('boardSet')
    expect(wrapper.emitted('boardSet')).toBeTruthy()
  })

  it('emits linkJumpSet event', () => {
    const wrapper = mountMenu()
    const vm = wrapper.vm as any
    vm.$emit('linkJumpSet')
    expect(wrapper.emitted('linkJumpSet')).toBeTruthy()
  })
})
