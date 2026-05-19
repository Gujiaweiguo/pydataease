import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: { get: vi.fn(() => null), set: vi.fn() }
  })
}))
vi.mock('@/store/modules/data-visualization/dvMain', () => {
  const dvInfo = { value: { id: null }, __v_isRef: true }
  return {
    dvMainStoreWithOut: () => ({ dvInfo, resetDvInfo: vi.fn() })
  }
})
vi.mock('@/store/modules/interactive', () => ({
  interactiveStoreWithOut: () => ({
    setInteractive: vi.fn(() => Promise.resolve()),
    getPanel: { treeNodes: [], rootManage: false, anyManage: false }
  })
}))
vi.mock('@/api/common', () => ({ getDefaultSettings: vi.fn(() => Promise.resolve({})) }))
vi.mock('vue-router_2', () => ({ useRouter: () => ({ push: vi.fn() }) }))
vi.mock('vant/es/sticky', () => ({ default: { template: '<div><slot /></div>' } }))
vi.mock('vant/es/nav-bar', () => ({ default: { template: '<div><slot /></div>' } }))
vi.mock('vant/es/sticky/style', () => ({}))
vi.mock('vant/es/nav-bar/style', () => ({}))
vi.mock('lodash-es', () => ({ cloneDeep: (v: any) => JSON.parse(JSON.stringify(v)) }))
vi.mock('@/utils/treeSortUtils', () => ({ default: vi.fn((data: any) => data) }))
vi.mock('@/assets/svg/dv-folder.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_dashboard.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_right_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_search-outline_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/dv-sort-asc.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/dv-sort-desc.svg', () => ({ default: '' }))
import MobileDirectory from '../index.vue'

describe('MobileDirectory', () => {
  const stubs = {
    VanSticky: { template: '<div><slot /></div>' },
    VanNavBar: { template: '<div><slot /></div>' },
    ElInput: { template: '<input />', props: ['modelValue'] },
    ElIcon: { template: '<i><slot /></i>' },
    ElDropdown: { template: '<div><slot /><slot name="dropdown" /></div>' },
    ElDropdownMenu: { template: '<ul><slot /></ul>' },
    ElDropdownItem: { template: '<li><slot /></li>' },
    DashboardCell: { template: '<div />' }
  }

  it('renders mobile dashboard container', () => {
    const wrapper = shallowMount(MobileDirectory, {
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('has mobile-dashboard class', () => {
    const wrapper = shallowMount(MobileDirectory, {
      global: { stubs }
    })
    expect(wrapper.find('.mobile-dashboard').exists()).toBe(true)
  })

  it('renders dashboard cell group', () => {
    const wrapper = shallowMount(MobileDirectory, {
      global: { stubs }
    })
    expect(wrapper.find('.dashboard-cell-group').exists()).toBe(true)
  })
})
