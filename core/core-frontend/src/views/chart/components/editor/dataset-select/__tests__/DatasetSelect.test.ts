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

vi.mock('@/store/modules/app', () => ({
  useAppStoreWithOut: () => ({
    getDekey: 'dekey',
    getIsDataEaseBi: false,
    getIsIframe: false
  })
}))

vi.mock('@/store/modules/user', () => ({
  useUserStoreWithOut: () => ({
    getOid: '1'
  })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    curComponent: null
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

vi.mock('@/api/dataset', () => ({
  getDatasetTree: vi.fn(() => Promise.resolve([])),
  getDatasourceList: vi.fn(() => Promise.resolve([]))
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: vi.fn(() => ({
    emitter: { emit: vi.fn() }
  }))
}))

vi.mock('@/utils/treeSortUtils', () => ({
  default: vi.fn((arr: any[]) => arr)
}))

vi.mock('@/assets/svg/dv-folder.svg', () => ({}))
vi.mock('@/assets/svg/icon_dataset.svg', () => ({}))
vi.mock('@/assets/svg/icon_done_outlined.svg', () => ({}))
vi.mock('@/views/visualized/data/dataset/form/CreatDsGroup.vue', () => ({
  Tree: {}
}))

vi.mock('lodash', () => ({
  default: {
    cloneDeep: vi.fn((v: any) => JSON.parse(JSON.stringify(v))),
    forEach: vi.fn(),
    filter: vi.fn(() => []),
    find: vi.fn(),
    union: vi.fn()
  }
}))

describe('DatasetSelect', () => {
  it('renders without errors', async () => {
    const DatasetSelect = (await import('../DatasetSelect.vue')).default
    const wrapper = shallowMount(DatasetSelect, {
      props: {
        stateObj: {},
        viewId: 'test-view-id',
        modelValue: '',
        themes: 'dark'
      },
      global: {
        stubs: {
          'el-popover': {
            template: '<div class="popover-stub"><slot name="reference" /><slot /></div>'
          },
          'el-form': {
            template: '<form><slot /></form>',
            methods: { validate: () => Promise.resolve() }
          },
          'el-form-item': { template: '<div><slot /></div>' },
          'el-input': { template: '<input />' },
          'el-icon': { template: '<span><slot /></span>' },
          Icon: { template: '<span><slot /></span>' }
        }
      }
    })
    await new Promise(r => setTimeout(r, 50))
    expect(wrapper.find('.popover-stub').exists() || wrapper.find('input').exists()).toBe(true)
  })
})
