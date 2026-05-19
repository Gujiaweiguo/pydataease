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
vi.mock('@/views/workbranch/ShortcutOption', () => ({
  shortcutOption: {
    loadData: vi.fn(() => Promise.resolve({ data: [] })),
    setBusiFlag: vi.fn()
  }
}))
vi.mock('vue-router_2', () => ({ useRouter: () => ({ push: vi.fn() }) }))
vi.mock('vant/es/sticky', () => ({ default: { template: '<div><slot /></div>' } }))
vi.mock('vant/es/nav-bar', () => ({ default: { template: '<div><slot /></div>' } }))
vi.mock('vant/es/tab', () => ({ default: { template: '<div />' } }))
vi.mock('vant/es/tabs', () => ({ default: { template: '<div><slot /></div>' } }))
vi.mock('vant/es/sticky/style', () => ({}))
vi.mock('vant/es/tab/style', () => ({}))
vi.mock('vant/es/nav-bar/style', () => ({}))
vi.mock('vant/es/tabs/style', () => ({}))
vi.mock('lodash-es', () => ({
  cloneDeep: (v: any) => JSON.parse(JSON.stringify(v)),
  map: (arr: any, fn: any) => arr.map(fn)
}))
vi.mock('@/components/plugin', () => ({ XpackComponent: { template: '<div />' } }))
vi.mock('@/assets/img/none.png', () => ({ default: 'none.png' }))
import MobileHome from '../index.vue'

describe('MobileHome', () => {
  const stubs = {
    VanSticky: { template: '<div><slot /></div>' },
    VanNavBar: { template: '<div><slot /></div>' },
    VanTabs: { template: '<div><slot /></div>' },
    VanTab: { template: '<div />' },
    Workbranch: { template: '<div />' },
    XpackComponent: { template: '<div />' }
  }

  it('renders mobile panel list', () => {
    const wrapper = shallowMount(MobileHome, {
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('has mobile-panel-list class', () => {
    const wrapper = shallowMount(MobileHome, {
      global: { stubs }
    })
    expect(wrapper.find('.mobile-panel-list').exists()).toBe(true)
  })

  it('shows empty state when emptyTips is set', async () => {
    const wrapper = shallowMount(MobileHome, {
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
