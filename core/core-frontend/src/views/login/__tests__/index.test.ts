import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: { get: vi.fn(() => null), set: vi.fn() }
  })
}))
vi.mock('@/store/modules/app', () => ({
  useAppStoreWithOut: () => ({ getDekey: 'de-key' })
}))
vi.mock('@/store/modules/user', () => ({
  useUserStoreWithOut: () => ({
    setToken: vi.fn(),
    setExp: vi.fn(),
    setTime: vi.fn(),
    getUid: '1'
  })
}))
vi.mock('@/store/modules/appearance', () => ({
  useAppearanceStoreWithOut: () => ({
    getBg: null,
    getLogin: null,
    getShowSlogan: null,
    getSlogan: null,
    getFoot: null,
    getFootContent: null,
    getShowDemoTips: false,
    getDemoTipsContent: ''
  })
}))
vi.mock('@/store/modules/permission', () => ({
  usePermissionStoreWithOut: () => ({ clear: vi.fn() })
}))
vi.mock('@/api/login', () => ({
  loginApi: vi.fn(() => Promise.resolve({ data: { token: 'test', exp: 0 } })),
  queryDekey: vi.fn(() => Promise.resolve({ data: {} }))
}))
vi.mock('@/api/user', () => ({
  personInfoApi: vi.fn(() => Promise.resolve({ data: {} }))
}))
vi.mock('@/utils/encryption', () => ({ rsaEncryp: (v: string) => v }))
vi.mock('@/utils/logout', () => ({ logoutHandler: vi.fn() }))
vi.mock('@/utils/utils', () => ({ cleanPlatformFlag: vi.fn() }))
vi.mock('@/components/icon-custom', () => ({
  Icon: { template: '<div><slot /></div>' }
}))
vi.mock('@/components/custom-password', () => ({
  CustomPassword: { template: '<input />', props: ['modelValue'] }
}))
vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div />' }
}))
vi.mock('@/router', () => ({
  default: { push: vi.fn(), currentRoute: { value: { query: {} } } }
}))
vi.mock('element-resize-detector', () => ({
  default: () => ({ listenTo: vi.fn() })
}))
vi.mock('@/assets/svg/DataEase.svg', () => ({ default: '' }))
vi.mock('@/assets/login-desc-de.png', () => ({ default: '' }))

import Login from '../index.vue'

describe('Login', () => {
  const stubs = {
    ElForm: { template: '<form><slot /></form>', props: ['model', 'rules', 'size', 'disabled'] },
    ElFormItem: { template: '<div><slot /></div>', props: ['prop', 'label', 'class'] },
    ElInput: { template: '<input />', props: ['modelValue', 'placeholder', 'autofocus'] },
    ElButton: { template: '<button><slot /></button>', props: ['type', 'size', 'disabled'] },
    ElImage: { template: '<img />', props: ['src', 'fit'] },
    ElMessage: { success: vi.fn(), error: vi.fn(), warning: vi.fn() },
    XpackComponent: { template: '<div />' },
    Icon: { template: '<div><slot /></div>' },
    CustomPassword: { template: '<input />', props: ['modelValue'] }
  }

  it('renders component', () => {
    const wrapper = shallowMount(Login, {
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('has login-background class', () => {
    const wrapper = shallowMount(Login, {
      global: { stubs }
    })
    expect(wrapper.find('.login-background').exists()).toBe(true)
  })
})
