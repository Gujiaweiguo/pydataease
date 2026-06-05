import { flushPromises, shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockPush, mockResolve, mockSearchMarketRecommend, mockQueryShareBaseApi, mockWindowOpen } =
  vi.hoisted(() => ({
    mockPush: vi.fn(),
    mockResolve: vi.fn(() => ({ href: '/dataset-form' })),
    mockSearchMarketRecommend: vi.fn(() =>
      Promise.resolve({
        data: {
          baseUrl: '',
          contents: []
        }
      })
    ),
    mockQueryShareBaseApi: vi.fn(() => Promise.resolve({ data: {} })),
    mockWindowOpen: vi.fn()
  }))

const interactiveData = {
  0: { menuAuth: true, leafNodeCount: 1, anyManage: true, rootManage: true },
  1: { menuAuth: true, leafNodeCount: 1, anyManage: true, rootManage: true },
  2: { menuAuth: true, leafNodeCount: 12, anyManage: true, rootManage: true },
  3: { menuAuth: true, leafNodeCount: 3, anyManage: true, rootManage: true }
}

vi.mock('@/hooks/web/useI18n', () => ({
  t: (key: string) => key,
  useI18n: () => ({ t: (key: string) => key })
}))

vi.mock('@/config/axios', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

vi.mock('@/store/modules/interactive', () => ({
  interactiveStoreWithOut: () => ({
    getData: interactiveData
  })
}))

vi.mock('@/store/modules/permission', () => ({
  usePermissionStoreWithOut: () => ({ currentPath: '/workbranch' })
}))

vi.mock('@/store/modules/request', () => ({
  useRequestStoreWithOut: () => ({ loadingMap: {} })
}))

vi.mock('@/store/modules/user', () => ({
  useUserStoreWithOut: () => ({ getName: 'Administrator', getUid: 1 })
}))

vi.mock('vue-router_2', () => ({
  useRouter: () => ({ push: mockPush, resolve: mockResolve })
}))

vi.mock('@/api/templateMarket', () => ({
  searchMarketRecommend: mockSearchMarketRecommend
}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: { get: vi.fn(() => '1'), set: vi.fn() }
  })
}))

vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => ({ baseUrl: '', clearState: vi.fn() })
}))

vi.mock('@/store/modules/app', () => ({
  useAppStoreWithOut: () => ({ getIsDataEaseBi: false, getIsIframe: false })
}))

vi.mock('@/store/modules/share', () => ({
  useShareStoreWithOut: () => ({ setData: vi.fn() })
}))

vi.mock('@/api/visualization/dataVisualization', () => ({
  queryShareBaseApi: mockQueryShareBaseApi
}))

vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div />' }
}))

vi.mock('@/views/workbranch/TemplateBranchItem.vue', () => ({
  default: { template: '<div />' }
}))

vi.mock('@/views/workbranch/TemplateBranchItemSkeleton.vue', () => ({
  default: { template: '<div />' }
}))

vi.mock('@/views/workbranch/ShortcutTable.vue', () => ({
  default: { template: '<div />' }
}))

vi.mock('@/views/common/DeResourceCreateOptV2.vue', () => ({
  default: { template: '<div />' }
}))

vi.mock('@/assets/svg/icon_app_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_dashboard_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_database_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_operation-analysis_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/user-img.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_template_colorful.svg', () => ({ default: '' }))

import WorkbranchIndex from '../index.vue'

describe('workbranch index counter navigation', () => {
  const stubs = {
    ElRow: { template: '<div><slot /></div>' },
    ElButton: { template: '<button><slot /></button>' },
    ElDivider: { template: '<div />' },
    ElScrollbar: { template: '<div><slot /></div>' },
    ElTooltip: { template: '<div><slot /></div>' },
    ElIcon: { template: '<i><slot /></i>' },
    Icon: { template: '<span><slot /></span>' },
    no_result: { template: '<span />' }
  }

  beforeEach(() => {
    vi.clearAllMocks()
    interactiveData[0].menuAuth = true
    interactiveData[1].menuAuth = true
    interactiveData[2].menuAuth = true
    interactiveData[3].menuAuth = true
    mockSearchMarketRecommend.mockResolvedValue({ data: { baseUrl: '', contents: [] } })
    mockQueryShareBaseApi.mockResolvedValue({ data: {} })
    vi.stubGlobal('open', mockWindowOpen)
  })

  it('navigates to panel index when the dashboard count is clicked with permission', async () => {
    const wrapper = shallowMount(WorkbranchIndex, {
      global: { stubs }
    })

    await flushPromises()
    const clickableCounts = wrapper.findAll('.count-card-clickable')

    await clickableCounts[0].trigger('click')

    expect(mockWindowOpen).toHaveBeenCalledWith('#/panel/index', '_self')
  })

  it('does not navigate when the dataset count has no permission', async () => {
    interactiveData[2].menuAuth = false

    const wrapper = shallowMount(WorkbranchIndex, {
      global: { stubs }
    })

    await flushPromises()
    const countItems = wrapper.findAll('.user-info .item')
    const datasetCount = countItems[2].find('.num')

    await datasetCount.trigger('click')

    expect(datasetCount.text()).toBe('*')
    expect(datasetCount.classes()).not.toContain('count-card-clickable')
    expect(mockPush).not.toHaveBeenCalled()
    expect(mockWindowOpen).not.toHaveBeenCalled()
  })
})
