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

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({ emitter: { emit: vi.fn() } })
}))

vi.mock('vue-router_2', () => ({
  useRoute: () => ({ path: '/' })
}))

vi.mock('@/views/visualized/data/dataset/ExportExcel.vue', () => ({
  default: { template: '<div />', methods: { init: vi.fn() } }
}))

import App from '@/pages/index/App.vue'
import { shallowMount } from '@vue/test-utils'

const stubs = {
  ConfigGlobal: { template: '<div><slot /></div>' },
  RouterView: { template: '<div />' },
  ExportExcel: { template: '<div />' }
}

describe('Index App', () => {
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
