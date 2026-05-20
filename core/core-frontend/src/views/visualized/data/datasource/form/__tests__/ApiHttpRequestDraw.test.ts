import { shallowMount } from '@vue/test-utils'
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

vi.mock('element-plus-secondary', () => ({
  ElIcon: { template: '<i><slot /></i>' },
  ElMessage: { success: vi.fn(), error: vi.fn(), warning: vi.fn() },
  ElMessageBox: { confirm: vi.fn() }
}))

vi.mock('@/api/datasource', () => ({
  checkApiItem: vi.fn(() => Promise.resolve({ data: {} }))
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

vi.mock('@/components/empty-background/src/EmptyBackground.vue', () => ({
  default: { template: '<div><slot /></div>' }
}))

vi.mock('@/components/plugin', () => ({
  PluginComponent: { template: '<div><slot /></div>' }
}))

vi.mock('./ApiHttpRequestForm.vue', () => ({
  default: { template: '<div>ApiHttpRequestForm</div>' }
}))

vi.mock('js-base64', () => ({
  Base64: { encode: vi.fn((s: string) => s), decode: vi.fn((s: string) => s) }
}))

vi.mock('lodash-es', () => ({
  cloneDeep: vi.fn((v: any) => JSON.parse(JSON.stringify(v)))
}))

vi.mock('@/assets/svg/icon_expand-right_filled.svg', () => ({ default: 'expand-icon' }))

import ApiHttpRequestDraw from '../ApiHttpRequestDraw.vue'

const globalStubs = {
  'el-form': true,
  'el-form-item': true,
  'el-input': true,
  'el-select': true,
  'el-option': true,
  'el-button': true,
  'el-dialog': true,
  'el-table': true,
  'el-table-column': true,
  'el-icon': true,
  'el-tooltip': true,
  'el-popover': true,
  'el-steps': true,
  'el-step': true,
  'el-row': true,
  'el-checkbox': true,
  'el-input-number': true,
  'el-table-v2': true,
  'el-auto-resizer': true,
  'el-drawer': true
}

describe('ApiHttpRequestDraw', () => {
  const mountComponent = () =>
    shallowMount(ApiHttpRequestDraw, {
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
