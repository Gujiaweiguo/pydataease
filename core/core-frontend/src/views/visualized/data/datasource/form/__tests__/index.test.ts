import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: vi.fn(() => ({ emitter: { on: vi.fn(), off: vi.fn(), emit: vi.fn() } }))
}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: { get: vi.fn(), set: vi.fn() }
  })
}))

vi.mock('@/api/datasource', () => ({
  listDatasources: vi.fn(() => Promise.resolve({ data: [] })),
  save: vi.fn(() => Promise.resolve({ data: {} })),
  update: vi.fn(() => Promise.resolve({ data: {} })),
  getSchema: vi.fn(() => Promise.resolve({ data: [] })),
  validate: vi.fn(() => Promise.resolve({ data: { success: true } })),
  latestUse: vi.fn(() => Promise.resolve({ data: [] })),
  isShowFinishPage: vi.fn(() => Promise.resolve({ data: false })),
  checkRepeat: vi.fn(() => Promise.resolve({ data: false })),
  loadRemoteFile: vi.fn(() => Promise.resolve({ data: {} }))
}))

vi.mock('element-plus-secondary', () => ({
  ElIcon: { template: '<i><slot /></i>' },
  ElMessage: { success: vi.fn(), error: vi.fn(), warning: vi.fn() },
  ElMessageBox: { confirm: vi.fn() },
  ElMessageBoxOptions: {}
}))

vi.mock('@/components/icon-custom', () => ({
  Icon: { template: '<i><slot /></i>' }
}))

vi.mock('@/components/icon-custom/src/Icon.vue', () => ({
  default: { template: '<i><slot /></i>' }
}))

vi.mock('@/components/icon-group/datasource-list', () => ({
  iconDatasourceMap: {}
}))

vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div><slot /></div>' },
  PluginComponent: { template: '<div><slot /></div>' }
}))

vi.mock('./CreatDsGroup.vue', () => ({
  default: { template: '<div>CreatDsGroup</div>' }
}))

vi.mock('./DsTypeList.vue', () => ({
  default: { template: '<div>DsTypeList</div>' }
}))

vi.mock('./EditorDetail.vue', () => ({
  default: { template: '<div>EditorDetail</div>' }
}))

vi.mock('./ExcelDetail.vue', () => ({
  default: { template: '<div>ExcelDetail</div>' }
}))

vi.mock('./ExcelRemoteDetail.vue', () => ({
  default: { template: '<div>ExcelRemoteDetail</div>' }
}))

vi.mock('../FinishPage.vue', () => ({
  default: { template: '<div>FinishPage</div>' }
}))

vi.mock('js-base64', () => ({
  Base64: { encode: vi.fn((s: string) => s), decode: vi.fn((s: string) => s) }
}))

vi.mock('lodash-es', () => ({
  cloneDeep: vi.fn((v: any) => JSON.parse(JSON.stringify(v)))
}))

vi.mock('vue-router_2', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    currentRoute: { value: { query: {} } }
  })),
  createRouter: vi.fn(() => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
    beforeEach: vi.fn(),
    afterEach: vi.fn(),
    currentRoute: { value: { query: {} } }
  })),
  createWebHashHistory: vi.fn(() => ({}))
}))

vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

vi.mock('@/store', () => ({
  store: {}
}))

vi.mock('pinia', () => ({
  defineStore: vi.fn(),
  storeToRefs: vi.fn(() => ({})),
  createPinia: vi.fn()
}))

vi.mock('vue-uuid', () => ({
  uuid: vi.fn(() => 'test-uuid-1234')
}))

vi.mock('@/assets/svg/icon_close_outlined.svg', () => ({ default: 'close-icon' }))
vi.mock('@/assets/svg/icon_search-outline_outlined.svg', () => ({ default: 'search-icon' }))

import IndexForm from '../index.vue'

const globalStubs = {
  'el-input': { template: '<input />' },
  'el-button': { template: '<button><slot /></button>' },
  'el-dialog': { template: '<div class="el-dialog"><slot /></div>' },
  'el-icon': { template: '<i><slot /></i>' },
  'el-scrollbar': { template: '<div><slot /></div>' }
}

describe('index.vue datasource form', () => {
  const mountComponent = () =>
    shallowMount(IndexForm, {
      global: {
        stubs: globalStubs,
        mocks: {
          $t: (k: string) => k
        }
      }
    })

  it('renders', () => {
    const wrapper = mountComponent()
    expect(wrapper.exists()).toBe(true)
  })

  it('has a wrapper element', () => {
    const wrapper = mountComponent()
    expect(wrapper.element).toBeTruthy()
  })
})
