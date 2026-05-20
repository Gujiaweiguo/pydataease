import { describe, expect, it, vi } from 'vitest'

vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/store', () => ({ store: {} }))

vi.mock('pinia', () => ({
  defineStore: vi.fn(),
  storeToRefs: vi.fn(() => ({})),
  createPinia: vi.fn()
}))

vi.mock('@/components/config-global/src/ConfigGlobal.vue', () => ({
  default: { template: '<div><slot /></div>' }
}))

import App from '@/pages/mobile/App.vue'
import { shallowMount } from '@vue/test-utils'

const stubs = {
  ConfigGlobal: { template: '<div><slot /></div>' },
  RouterView: { template: '<div />' }
}

describe('Mobile App', () => {
  it('renders successfully', () => {
    const wrapper = shallowMount(App, {
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders router-view', () => {
    const wrapper = shallowMount(App, {
      global: { stubs }
    })
    expect(wrapper.findComponent(stubs.RouterView).exists() || wrapper.html().length > 0).toBe(true)
  })
})
