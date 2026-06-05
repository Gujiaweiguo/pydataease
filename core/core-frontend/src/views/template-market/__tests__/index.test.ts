import { flushPromises, shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  mockSearchMarket,
  mockFindCategoriesByTemplateIds,
  mockTemplateDelete,
  mockConfirm,
  mockSuccess,
  mockGetActiveCategories
} = vi.hoisted(() => ({
  mockSearchMarket: vi.fn(),
  mockFindCategoriesByTemplateIds: vi.fn(),
  mockTemplateDelete: vi.fn(),
  mockConfirm: vi.fn(),
  mockSuccess: vi.fn(),
  mockGetActiveCategories: vi.fn()
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: { get: vi.fn(() => null), set: vi.fn(), delete: vi.fn() }
  })
}))

vi.mock('@/api/templateMarket', () => ({
  searchMarket: mockSearchMarket
}))

vi.mock('@/api/template', () => ({
  exportTemplate: vi.fn(),
  templateDelete: mockTemplateDelete,
  findCategories: vi.fn(() => Promise.resolve({ data: [] })),
  findCategoriesByTemplateIds: mockFindCategoriesByTemplateIds
}))

vi.mock('element-plus-secondary', async importOriginal => {
  const actual = (await importOriginal()) as Record<string, unknown>
  return {
    ...actual,
    ElMessageBox: {
      confirm: mockConfirm
    },
    ElMessage: {
      success: mockSuccess,
      error: vi.fn(),
      warning: vi.fn()
    }
  }
})

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
    getActiveCategories: mockGetActiveCategories
  }
})

vi.mock('element-resize-detector', () => ({
  default: () => ({ listenTo: vi.fn() })
}))

vi.mock('@/utils/imgUtils', () => ({
  imgUrlTrans: (url: string) => url
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
    ElTree: {
      template: '<div />',
      props: ['data', 'props', 'nodeKey', 'defaultExpandAll', 'highlightCurrent', 'currentNodeKey']
    },
    ElIcon: { template: '<i><slot /></i>' }
  }

  const emptySearchMarketResponse = {
    data: {
      baseUrl: '',
      categories: [],
      contents: []
    }
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('handles empty categories without throwing', async () => {
    mockSearchMarket.mockResolvedValue(emptySearchMarketResponse)
    mockGetActiveCategories.mockReturnValue(new Set())
    const wrapper = shallowMount(TemplateMarketIndex, {
      global: { stubs }
    })
    await flushPromises()
    const vm = wrapper.vm as any
    expect(vm).toBeTruthy()
    expect(vm.state.marketTabs).toEqual([])
    expect(vm.state.marketActiveTab).toBe(null)
  })

  it('keeps the remaining category active after deleting the last dashboard template', async () => {
    mockConfirm.mockResolvedValue(undefined)
    mockSuccess.mockImplementation(() => undefined)
    mockFindCategoriesByTemplateIds.mockResolvedValue({ data: ['dashboard-category'] })
    mockTemplateDelete.mockResolvedValue({})
    mockGetActiveCategories.mockImplementation(contents => {
      return new Set(
        contents.flatMap((item: any) => item.categories.map((category: any) => category.name))
      )
    })
    mockSearchMarket
      .mockResolvedValueOnce({
        data: {
          baseUrl: '',
          categories: [{ label: '推荐' }, { label: '仪表板模板' }, { label: '大屏模板' }],
          contents: [
            {
              id: 'panel-template',
              title: 'Dashboard Save QA 20260603-C',
              templateType: 'PANEL',
              source: 'manage',
              classify: '推荐',
              showFlag: true,
              categoryNames: ['仪表板模板'],
              categories: [{ name: '仪表板模板' }]
            },
            {
              id: 'screen-template',
              title: 'Screen Save QA 20260603-A',
              templateType: 'SCREEN',
              source: 'manage',
              classify: '推荐',
              showFlag: true,
              categoryNames: ['大屏模板'],
              categories: [{ name: '大屏模板' }]
            }
          ]
        }
      })
      .mockResolvedValueOnce({
        data: {
          baseUrl: '',
          categories: [{ label: '推荐' }, { label: '大屏模板' }],
          contents: [
            {
              id: 'screen-template',
              title: 'Screen Save QA 20260603-A',
              templateType: 'SCREEN',
              source: 'manage',
              classify: '推荐',
              showFlag: true,
              categoryNames: ['大屏模板'],
              categories: [{ name: '大屏模板' }]
            }
          ]
        }
      })

    const wrapper = shallowMount(TemplateMarketIndex, {
      global: { stubs }
    })
    await flushPromises()

    const vm = wrapper.vm as any

    vm.state.marketActiveTab = '仪表板模板'
    await vm.handleTemplateDelete({ id: 'panel-template', title: 'Dashboard Save QA 20260603-C' })
    await flushPromises()

    expect(mockFindCategoriesByTemplateIds).toHaveBeenCalledWith({
      templateIds: ['panel-template']
    })
    expect(mockTemplateDelete).toHaveBeenCalledWith('panel-template', 'dashboard-category')
    expect(vm.state.marketTabs).toEqual([{ label: '大屏模板' }])
    expect(vm.state.marketActiveTab).toBe('大屏模板')
  })

  it('stays on the current category when it still exists after delete refresh', async () => {
    mockConfirm.mockResolvedValue(undefined)
    mockSuccess.mockImplementation(() => undefined)
    mockFindCategoriesByTemplateIds.mockResolvedValue({ data: ['dashboard-category'] })
    mockTemplateDelete.mockResolvedValue({})
    mockGetActiveCategories.mockImplementation(contents => {
      return new Set(
        contents.flatMap((item: any) => item.categories.map((category: any) => category.name))
      )
    })
    mockSearchMarket
      .mockResolvedValueOnce({
        data: {
          baseUrl: '',
          categories: [{ label: '推荐' }, { label: '仪表板模板' }, { label: '大屏模板' }],
          contents: [
            {
              id: 'panel-template-a',
              title: 'Dashboard Save QA 20260603-A',
              templateType: 'PANEL',
              source: 'manage',
              classify: '推荐',
              showFlag: true,
              categoryNames: ['仪表板模板'],
              categories: [{ name: '仪表板模板' }]
            },
            {
              id: 'panel-template-b',
              title: 'Dashboard Save QA 20260603-B',
              templateType: 'PANEL',
              source: 'manage',
              classify: '推荐',
              showFlag: true,
              categoryNames: ['仪表板模板'],
              categories: [{ name: '仪表板模板' }]
            },
            {
              id: 'screen-template',
              title: 'Screen Save QA 20260603-A',
              templateType: 'SCREEN',
              source: 'manage',
              classify: '推荐',
              showFlag: true,
              categoryNames: ['大屏模板'],
              categories: [{ name: '大屏模板' }]
            }
          ]
        }
      })
      .mockResolvedValueOnce({
        data: {
          baseUrl: '',
          categories: [{ label: '推荐' }, { label: '仪表板模板' }, { label: '大屏模板' }],
          contents: [
            {
              id: 'panel-template-b',
              title: 'Dashboard Save QA 20260603-B',
              templateType: 'PANEL',
              source: 'manage',
              classify: '推荐',
              showFlag: true,
              categoryNames: ['仪表板模板'],
              categories: [{ name: '仪表板模板' }]
            },
            {
              id: 'screen-template',
              title: 'Screen Save QA 20260603-A',
              templateType: 'SCREEN',
              source: 'manage',
              classify: '推荐',
              showFlag: true,
              categoryNames: ['大屏模板'],
              categories: [{ name: '大屏模板' }]
            }
          ]
        }
      })

    const wrapper = shallowMount(TemplateMarketIndex, {
      global: { stubs }
    })
    await flushPromises()

    const vm = wrapper.vm as any

    vm.state.marketActiveTab = '仪表板模板'
    await vm.handleTemplateDelete({ id: 'panel-template-a', title: 'Dashboard Save QA 20260603-A' })
    await flushPromises()

    expect(mockFindCategoriesByTemplateIds).toHaveBeenCalledWith({
      templateIds: ['panel-template-a']
    })
    expect(mockTemplateDelete).toHaveBeenCalledWith('panel-template-a', 'dashboard-category')
    expect(vm.state.marketTabs).toEqual([{ label: '仪表板模板' }, { label: '大屏模板' }])
    expect(vm.state.marketActiveTab).toBe('仪表板模板')
  })
})
