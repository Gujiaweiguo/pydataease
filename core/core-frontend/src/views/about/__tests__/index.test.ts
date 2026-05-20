import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: { get: vi.fn(() => null), set: vi.fn() }
  })
}))
vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: vi.fn()
}))
vi.mock('@/store/modules/user', () => ({
  useUserStoreWithOut: () => ({ getUid: '1' })
}))
vi.mock('@/api/about', () => ({
  validateApi: vi.fn(() => Promise.resolve({ data: { status: 'valid', license: {} } })),
  buildVersionApi: vi.fn(() => Promise.resolve({ data: 'v1.0' })),
  updateInfoApi: vi.fn(() => Promise.resolve({ data: { status: 'valid', license: {} } })),
  revertApi: vi.fn(() => Promise.resolve())
}))
vi.mock('@/api/login', () => ({
  logoutApi: vi.fn(() => Promise.resolve())
}))
vi.mock('@/utils/logout', () => ({ logoutHandler: vi.fn() }))
vi.mock('@/assets/svg/logo.svg', () => ({ default: '' }))
vi.mock('@/assets/img/about-bg.png', () => ({ default: '' }))

import About from '../index.vue'

describe('About', () => {
  const stubs = {
    ElDialog: { template: '<div><slot /></div>', props: ['modelValue', 'title', 'width', 'class'] },
    ElIcon: { template: '<i><slot /></i>' },
    ElUpload: {
      template: '<div><slot /></div>',
      props: ['action', 'accept', 'name', 'beforeUpload']
    },
    ElButton: { template: '<button><slot /></button>', props: ['plain'] },
    icon: { template: '<div><slot /></div>' }
  }

  const globalConfig = {
    stubs,
    mocks: { $t: (k: string) => k }
  }

  it('renders component', () => {
    const wrapper = shallowMount(About, { global: globalConfig })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders dialog content area', () => {
    const wrapper = shallowMount(About, { global: globalConfig })
    expect(wrapper.find('.content').exists()).toBe(true)
  })
})
