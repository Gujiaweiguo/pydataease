import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: vi.fn(() => ({ emitter: { on: vi.fn(), off: vi.fn(), emit: vi.fn() } }))
}))

vi.mock('@/api/datasource', () => ({
  save: vi.fn(() => Promise.resolve({ data: {} })),
  update: vi.fn(() => Promise.resolve({ data: {} })),
  uploadFile: vi.fn(() => Promise.resolve({ data: {} }))
}))

vi.mock('@/utils/attr', () => ({
  fieldType: { TEXT: 0, NUMBER: 1 }
}))

vi.mock('@/components/icon-custom', () => ({
  Icon: { template: '<i><slot /></i>' }
}))

vi.mock('@/components/icon-group/field-list', () => ({
  iconFieldMap: {}
}))

vi.mock('@/views/visualized/data/datasource/ExcelInfo.vue', () => ({
  default: { template: '<div>ExcelInfo</div>' }
}))

vi.mock('@/views/visualized/data/datasource/SheetTabs.vue', () => ({
  default: { template: '<div>SheetTabs</div>' }
}))

vi.mock('element-plus-secondary', () => ({
  ElIcon: { template: '<i><slot /></i>' },
  ElMessage: { success: vi.fn(), error: vi.fn(), warning: vi.fn() },
  ElMessageBox: { confirm: vi.fn() }
}))

vi.mock('js-base64', () => ({
  Base64: { encode: vi.fn((s: string) => s), decode: vi.fn((s: string) => s) }
}))

vi.mock('lodash-es', () => ({
  cloneDeep: vi.fn((v: any) => JSON.parse(JSON.stringify(v))),
  debounce: vi.fn((fn: any) => fn)
}))

vi.mock('mathjs', () => ({
  boolean: vi.fn()
}))

vi.mock('@/assets/svg/icon_upload_outlined.svg', () => ({ default: 'upload-icon' }))

import ExcelDetail from '../ExcelDetail.vue'

const globalStubs = {
  'el-form': { template: '<form><slot /></form>' },
  'el-form-item': { template: '<div><slot /></div>' },
  'el-input': { template: '<input />' },
  'el-button': { template: '<button><slot /></button>' },
  'el-dialog': { template: '<div class="el-dialog"><slot /></div>' },
  'el-table': { template: '<table><slot /></table>' },
  'el-table-column': { template: '<td><slot /></td>' },
  'el-icon': { template: '<i><slot /></i>' },
  'el-tooltip': { template: '<span><slot /></span>' },
  'el-checkbox': { template: '<input type="checkbox" />' },
  'el-tag': { template: '<span><slot /></span>' },
  'el-dropdown': { template: '<div><slot /></div>' },
  'el-dropdown-menu': { template: '<div><slot /></div>' },
  'el-dropdown-item': { template: '<div><slot /></div>' }
}

describe('ExcelDetail', () => {
  const mountComponent = () =>
    shallowMount(ExcelDetail, {
      props: {
        param: {
          id: '0',
          name: '',
          desc: '',
          type: 'Excel',
          editType: 0
        },
        isSupportSetKey: false
      },
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
