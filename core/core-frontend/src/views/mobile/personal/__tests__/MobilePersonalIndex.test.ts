import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

vi.mock('@/config/axios/service', () => ({ service: {} as any, PATH_URL: './', cancelMap: new Map() }))
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/store', () => ({ store: {} }))
vi.mock('pinia', () => ({ defineStore: vi.fn(), storeToRefs: vi.fn(() => ({})), createPinia: vi.fn() }))

vi.mock('@/store/modules/user', () => ({
  useUserStoreWithOut: () => ({
    name: 'Test User',
    getOid: '1',
    setToken: vi.fn(),
    setExp: vi.fn(),
    setTime: vi.fn()
  })
}))

vi.mock('@/api/user', () => ({
  mountedOrg: vi.fn(() => Promise.resolve({ data: [] })),
  switchOrg: vi.fn(() => Promise.resolve({ data: { token: 'tok', exp: 1 } }))
}))

vi.mock('@/api/login', () => ({
  logoutApi: vi.fn(() => Promise.resolve())
}))

vi.mock('@/utils/logout', () => ({
  logoutHandler: vi.fn()
}))

vi.mock('vue-router_2', () => ({
  useRouter: () => ({ push: vi.fn() })
}))

vi.mock('@/views/system/modify-pwd/UpdatePwd.vue', () => ({
  default: { template: '<div class="update-pwd-stub" />' }
}))

vi.mock('@/views/mobile/components/OrgCell.vue', () => ({
  default: { template: '<div class="org-cell-stub" />' }
}))

vi.mock('vant/es/popup', () => ({ default: { template: '<div class="van-popup-stub"><slot /></div>' } }))
vi.mock('vant/es/nav-bar', () => ({ default: { template: '<div class="van-nav-bar-stub" />' } }))
vi.mock('vant/es/image', () => ({ default: { template: '<div class="van-image-stub" />' } }))
vi.mock('vant/es/image/style', () => ({}))
vi.mock('vant/es/nav-bar/style', () => ({}))
vi.mock('vant/es/popup/style', () => ({}))

vi.mock('@/assets/svg/icon_right_outlined.svg', () => ({ default: {} }))
vi.mock('@/assets/img/user.png', () => ({ default: 'user-img' }))

describe('MobilePersonalIndex', () => {
  it('renders without errors', async () => {
    const MobilePersonal = (await import('../index.vue')).default
    const wrapper = shallowMount(MobilePersonal, {
      global: {
        mocks: {
          $t: (k: string) => k
        },
        stubs: {
          'org-cell': { template: '<div class="org-cell-stub" />' },
          'van-image': { template: '<div class="van-image-stub" />' },
          'van-popup': { template: '<div class="van-popup-stub"><slot /></div>' },
          'update-pwd': { template: '<div class="update-pwd-stub" />' },
          'van-nav-bar': { template: '<div class="van-nav-bar-stub" />' },
          'icon_right_outlined': { template: '<span />' },
          Icon: { template: '<span><slot /></span>' }
        }
      }
    })
    expect(wrapper.find('.de-mobile-user').exists()).toBe(true)
  })
})
