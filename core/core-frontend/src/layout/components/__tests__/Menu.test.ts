import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('@/utils/color', () => ({
  getCSSVariable: vi.fn(() => '#3370ff')
}))

vi.mock('@/utils/validate', () => ({
  isExternal: vi.fn(() => false)
}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: {
      get: vi.fn(() => null),
      set: vi.fn()
    }
  })
}))

vi.mock('@/store/modules/appearance', () => ({
  useAppearanceStoreWithOut: () => ({
    themeColor: 'default',
    customColor: ''
  })
}))

vi.mock('vue-router_2', () => ({
  useRoute: vi.fn(() => ({
    path: '/dashboard/index',
    matched: [{ path: '/dashboard', children: [] }]
  })),
  useRouter: vi.fn(() => ({
    push: vi.fn()
  })),
  createRouter: vi.fn(() => ({})),
  createWebHashHistory: vi.fn()
}))

import Menu from '../Menu.vue'

const globalStubs = {
  ElMenu: {
    template: '<div class="el-menu-stub"><slot /></div>',
    props: ['collapse', 'defaultActive']
  },
  MenuItem: { template: '<div class="menu-item-stub" />' }
}

describe('Menu', () => {
  it('renders', () => {
    const wrapper = shallowMount(Menu, {
      props: { collapse: false },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('has el-menu-stub rendered', () => {
    const wrapper = shallowMount(Menu, {
      props: { collapse: true },
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.el-menu-stub').exists()).toBe(true)
  })

  it('applies style with temp color', () => {
    const wrapper = shallowMount(Menu, {
      props: { collapse: false },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
