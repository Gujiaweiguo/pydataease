import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

vi.mock('./convert', () => ({
  execute: vi.fn(),
  randomKey: vi.fn(() => 10),
  formatArray: vi.fn((arr: number[]) => String.fromCharCode(...arr))
}))

vi.mock('@/api/plugin', () => ({
  load: vi.fn(() => Promise.resolve({ data: '' })),
  loadDistributed: vi.fn(() => Promise.resolve({ data: '' })),
  xpackModelApi: vi.fn(() => Promise.resolve({ data: null }))
}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: {
      get: vi.fn(() => null),
      set: vi.fn()
    }
  })
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({
    emitter: { all: new Map() }
  })
}))

vi.mock('@/plugins/vue-i18n', () => ({
  i18n: { global: { t: (k: string) => k } }
}))

vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => ({ baseUrl: '' })
}))

vi.mock('@/utils/utils', () => ({
  isNull: vi.fn((v: any) => v === null || v === undefined)
}))

vi.mock('@/components/config-global/src/ConfigGlobal.vue', () => ({
  default: { template: '<div><slot /></div>' }
}))

import PluginIndex from '../index.vue'

const mountComponent = () =>
  shallowMount(PluginIndex, {
    attrs: {
      jsname: 'dGVzdA=='
    },
    global: {
      stubs: {
        'config-global': { template: '<div><slot /></div>' }
      }
    }
  })

describe('Plugin index', () => {
  it('renders the component', () => {
    const wrapper = mountComponent()

    expect(wrapper.exists()).toBe(true)
  })

  it('exposes invokeMethod', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as unknown as { invokeMethod: (param: any) => void }

    expect(typeof vm.invokeMethod).toBe('function')
  })

  it('emits loadFail on failed xpack model', async () => {
    const wrapper = mountComponent()

    await new Promise(resolve => setTimeout(resolve, 1200))

    expect(wrapper.emitted('loadFail')).toBeTruthy()
  })
})
