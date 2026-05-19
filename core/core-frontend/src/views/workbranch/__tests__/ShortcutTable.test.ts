import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({ default: { post: vi.fn(() => Promise.resolve({ data: [] })) } }))
vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: { get: vi.fn(() => null), set: vi.fn() }
  })
}))
vi.mock('@/store/modules/interactive', () => ({
  interactiveStoreWithOut: () => ({
    getData: {},
    setInteractive: vi.fn(() => Promise.resolve())
  })
}))
vi.mock('@/store/modules/user', () => ({ useUserStoreWithOut: () => ({ getName: 'test' }) }))
vi.mock('@/store/modules/app', () => ({ useAppStoreWithOut: () => ({ getIsIframe: false }) }))
vi.mock('@/store/modules/embedded', () => ({ useEmbedded: () => ({ getToken: null }) }))
vi.mock('@/store/modules/share', () => ({
  useShareStoreWithOut: () => ({ getShareDisable: false })
}))
vi.mock('@/api/visualization/dataVisualization', () => ({
  storeApi: vi.fn(() => Promise.resolve())
}))
vi.mock('vue-router_2', () => ({
  useRouter: () => ({ push: vi.fn(), resolve: vi.fn(() => ({ href: '' })) })
}))
vi.mock('@/components/plugin', () => ({ XpackComponent: { template: '<div />' } }))
vi.mock('@/views/workbranch/ShortcutOption', () => ({
  shortcutOption: {
    loadData: vi.fn(() => Promise.resolve({ data: [] })),
    setBusiFlag: vi.fn(),
    getBusiList: vi.fn(() => ['all_types']),
    getColumnList: vi.fn(() => [])
  }
}))
vi.mock('lodash-es', () => ({ cloneDeep: (v: any) => JSON.parse(JSON.stringify(v)) }))
vi.mock('@/assets/svg/icon_collection_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/visual-star.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_search-outline_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_app_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_dashboard_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_database_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_operation-analysis_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/dv-dashboard-spine-mobile.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_pc_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/dv-dashboard-spine-mobile-disabled.svg', () => ({ default: '' }))
vi.mock('vue-clipboard3', () => ({
  default: () => ({ toClipboard: vi.fn(() => Promise.resolve()) })
}))
vi.mock('@/views/share/share/ShareGrid.vue', () => ({ default: { template: '<div />' } }))
vi.mock('@/views/share/share/ShareHandler.vue', () => ({ default: { template: '<div />' } }))
import ShortcutTable from '../ShortcutTable.vue'

describe('ShortcutTable', () => {
  const stubs = {
    ElTabs: { template: '<div><slot /></div>' },
    ElTabPane: { template: '<div><slot /></div>' },
    ElButton: { template: '<button><slot /></button>' },
    ElInput: { template: '<input />', props: ['modelValue'] },
    ElSelect: { template: '<select><slot /></select>' },
    ElOption: { template: '<option><slot /></option>' },
    ElRow: { template: '<div><slot /></div>' },
    ElCol: { template: '<div><slot /></div>' },
    ElIcon: { template: '<i><slot /></i>' },
    ElTooltip: { template: '<div><slot /></div>' },
    ElEmpty: { template: '<div />' },
    GridTable: { template: '<div><slot /></div>' },
    XpackComponent: { template: '<div />' },
    ShareGrid: { template: '<div />' },
    ShareHandler: { template: '<div />' }
  }

  it('renders with default state', () => {
    const wrapper = shallowMount(ShortcutTable, {
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts expand prop', () => {
    const wrapper = shallowMount(ShortcutTable, {
      props: { expand: true },
      global: { stubs }
    })
    expect(wrapper.props('expand')).toBe(true)
  })

  it('has dashboard-type class container', () => {
    const wrapper = shallowMount(ShortcutTable, {
      global: { stubs }
    })
    expect(wrapper.find('.dashboard-type').exists()).toBe(true)
  })
})
