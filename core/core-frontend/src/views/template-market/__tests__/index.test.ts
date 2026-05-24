import { flushPromises, shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: { get: vi.fn(() => null), set: vi.fn(), delete: vi.fn() }
  })
}))

vi.mock('@/api/templateMarket', () => ({
  searchMarket: vi.fn(() =>
    Promise.resolve({
      data: {
        baseUrl: '',
        categories: [],
        contents: []
      }
    })
  )
}))

vi.mock('@/store/modules/interactive', () => ({
  interactiveStoreWithOut: () => ({
    getData: {
      0: { menuAuth: true, rootManage: true },
      1: { menuAuth: true, rootManage: true }
    }
  })
}))

vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => ({
    clearState: vi.fn(),
    setCreateType: vi.fn(),
    setTemplateParams: vi.fn(),
    setOpt: vi.fn(),
    setPid: vi.fn()
  })
}))

vi.mock('@/store/modules/app', () => ({
  useAppStoreWithOut: () => ({ getIsDataEaseBi: false, getIsIframe: false })
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({ emitter: { emit: vi.fn() } })
}))

vi.mock('@/utils/utils', async importOriginal => {
  const actual = (await importOriginal()) as Record<string, unknown>
  return {
    ...actual,
    getActiveCategories: () => new Set()
  }
})

vi.mock('element-resize-detector', () => ({
  default: () => ({ listenTo: vi.fn() })
}))

vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div />' }
}))

vi.mock('@/views/template-market/component/MarketPreviewV2.vue', () => ({
  default: { template: '<div />' }
}))

vi.mock('@/views/template-market/component/CategoryTemplateV2.vue', () => ({
  default: { template: '<div />' }
}))

vi.mock('@/views/template-market/component/TemplateSkeleton.vue', () => ({
  default: { template: '<div />' }
}))

import TemplateMarketIndex from '../index.vue'

describe('template-market index', () => {
  const stubs = {
    ElRow: { template: '<div><slot /></div>' },
    ElButton: { template: '<button><slot /></button>' },
    ElDivider: { template: '<div />' },
    ElInput: { template: '<input />', props: ['modelValue'] },
    ElSelect: { template: '<div><slot /></div>', props: ['modelValue'] },
    ElOption: { template: '<div />' },
    ElScrollbar: { template: '<div><slot /></div>' },
    ElTree: { template: '<div><slot /></div>' },
    ElIcon: { template: '<i><slot /></i>' }
  }

  it('handles empty categories without throwing', async () => {
    const wrapper = shallowMount(TemplateMarketIndex, {
      global: { stubs }
    })
    await flushPromises()
    const vm = wrapper.vm as any
    expect(vm).toBeTruthy()
    expect(vm.state.marketTabs).toEqual([])
    expect(vm.state.marketActiveTab).toBe(null)
  })
})
