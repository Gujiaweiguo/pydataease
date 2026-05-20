import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/store', () => ({ store: {} }))
vi.mock('pinia', () => ({
  defineStore: vi.fn(),
  storeToRefs: vi.fn(() => ({})),
  createPinia: vi.fn()
}))

vi.mock('@/store/modules/appearance', () => ({
  useAppearanceStoreWithOut: () => ({
    getMobileLogin: '',
    getMobileLoginBg: ''
  })
}))

vi.mock('@/store/modules/app', () => ({
  useAppStoreWithOut: () => ({
    getDekey: 'test-dekey',
    getIsDataEaseBi: false,
    getIsIframe: false
  })
}))

vi.mock('@/store/modules/user', () => ({
  useUserStoreWithOut: () => ({
    setToken: vi.fn(),
    setExp: vi.fn(),
    setTime: vi.fn()
  })
}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: {
      get: vi.fn(() => null),
      set: vi.fn()
    }
  })
}))

vi.mock('vue-router_2', () => ({
  useRouter: () => ({ push: vi.fn() })
}))

vi.mock('@/utils/encryption', () => ({
  rsaEncryp: vi.fn((v: string) => v)
}))

vi.mock('@/api/login', () => ({
  loginApi: vi.fn(() => Promise.resolve({ data: { token: 'tok', exp: 1 } })),
  queryDekey: vi.fn(() => Promise.resolve({ data: 'dekey' }))
}))

vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div class="xpack-stub" />' }
}))

vi.mock('vant', () => ({
  showToast: vi.fn()
}))

vi.mock('vant/es/form', () => ({
  default: { template: '<form class="van-form-stub"><slot /></form>' }
}))
vi.mock('vant/es/field', () => ({ default: { template: '<div class="van-field-stub" />' } }))
vi.mock('vant/es/button', () => ({
  default: { template: '<button class="van-button-stub"><slot /></button>' }
}))
vi.mock('vant/es/cell-group', () => ({
  default: { template: '<div class="van-cell-group-stub"><slot /></div>' }
}))
vi.mock('vant/es/button/style', () => ({}))
vi.mock('vant/es/toast/style', () => ({}))
vi.mock('vant/es/field/style', () => ({}))
vi.mock('vant/es/form/style', () => ({}))
vi.mock('vant/es/cell-group/style', () => ({}))

vi.mock('@/assets/svg/icon_invisible_outlined.svg', () => ({ default: {} }))
vi.mock('@/assets/svg/icon_visible_outlined.svg', () => ({ default: {} }))
vi.mock('@/assets/img/bg-mobile.png', () => ({ default: 'bg-mobile' }))
vi.mock('@/assets/img/mobile-de-top.png', () => ({ default: 'mobile-de-top' }))

describe('MobileLoginIndex', () => {
  it('renders without errors', async () => {
    const MobileLogin = (await import('../index.vue')).default
    const wrapper = shallowMount(MobileLogin, {
      global: {
        stubs: {
          'van-form': { template: '<form class="van-form-stub"><slot /></form>' },
          'van-cell-group': { template: '<div class="van-cell-group-stub"><slot /></div>' },
          'van-field': { template: '<div class="van-field-stub" />' },
          'van-button': { template: '<button class="van-button-stub"><slot /></button>' },
          'xpack-component': { template: '<div class="xpack-stub" />' },
          Icon: { template: '<span><slot /></span>' },
          icon_invisible_outlined: { template: '<span />' },
          icon_visible_outlined: { template: '<span />' }
        }
      }
    })
    expect(wrapper.find('.de-mobile-login').exists()).toBe(true)
  })
})
