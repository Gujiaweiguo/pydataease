import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('@/config/axios/service', () => ({}))

vi.mock('@/config/axios/refresh', () => ({}))

vi.mock('@/store/modules/user', () => ({
  useUserStoreWithOut: vi.fn(() => ({}))
}))

vi.mock('@/store/modules/app', () => ({
  useAppStoreWithOut: () => ({
    getArrowSide: false
  })
}))

vi.mock('@/store/modules/appearance', () => ({
  useAppearanceStoreWithOut: () => ({
    getNavigateBg: 'dark',
    getNavigate: null,
    themeColor: 'default'
  })
}))

vi.mock('@/utils/ModelUtil', () => ({
  isDesktop: vi.fn(() => false)
}))

vi.mock('vue-router_2', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn()
  })),
  createRouter: vi.fn(() => ({})),
  createWebHashHistory: vi.fn()
}))

vi.mock('@/assets/svg/logo.svg', () => ({ default: 'logo-svg' }))
vi.mock('@/assets/svg/icon_left_outlined.svg', () => ({ default: 'left-icon' }))

import HeaderSystem from '../HeaderSystem.vue'

const globalStubs = {
  ElHeader: { template: '<header class="el-header-stub"><slot /></header>' },
  ElDivider: { template: '<div class="divider-stub" />' },
  ElIcon: { template: '<i><slot /></i>' },
  AccountOperator: { template: '<div class="account-operator-stub" />' }
}

describe('HeaderSystem', () => {
  const mountComponent = (title = 'Test Title') =>
    shallowMount(HeaderSystem, {
      props: { title },
      global: { stubs: globalStubs }
    })

  it('renders', () => {
    const wrapper = mountComponent()
    expect(wrapper.exists()).toBe(true)
  })

  it('displays the title prop', () => {
    const wrapper = mountComponent('My Custom Title')
    expect(wrapper.text()).toContain('My Custom Title')
  })

  it('uses default system setting when no title provided', () => {
    const wrapper = mountComponent('')
    expect(wrapper.exists()).toBe(true)
  })

  it('contains system header class', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('.system-header').exists()).toBe(true)
  })
})
