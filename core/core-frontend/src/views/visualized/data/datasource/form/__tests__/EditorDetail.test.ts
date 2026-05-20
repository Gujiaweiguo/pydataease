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

vi.mock('@/api/datasource', () => ({
  getSchema: vi.fn(() => Promise.resolve({ data: [] }))
}))

vi.mock('@/utils/attr', () => ({
  fieldType: { TEXT: 0, NUMBER: 1 },
  fieldTypeText: { 0: 'TEXT', 1: 'NUMBER' }
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

vi.mock('@/components/custom-password', () => ({
  CustomPassword: { template: '<input type="password" />' }
}))

vi.mock('@/components/cron/src/Cron.vue', () => ({
  default: { template: '<div>Cron</div>' }
}))

vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div><slot /></div>' }
}))

vi.mock('./ApiHttpRequestDraw.vue', () => ({
  default: { template: '<div>ApiHttpRequestDraw</div>' }
}))

vi.mock('js-base64', () => ({
  Base64: { encode: vi.fn((s: string) => s), decode: vi.fn((s: string) => s) }
}))

vi.mock('lodash-es', () => ({
  cloneDeep: vi.fn((v: any) => JSON.parse(JSON.stringify(v)))
}))

vi.mock('mathjs', () => ({
  boolean: vi.fn()
}))

vi.mock('@/assets/svg/icon_calendar_outlined.svg', () => ({ default: 'calendar-icon' }))
vi.mock('@/assets/svg/icon_rename_outlined.svg', () => ({ default: 'rename-icon' }))
vi.mock('@/assets/svg/icon_down_outlined.svg', () => ({ default: 'down-icon' }))
vi.mock('@/assets/svg/icon_down_outlined-1.svg', () => ({ default: 'down-icon-1' }))
vi.mock('@/assets/svg/icon_add_outlined.svg', () => ({ default: 'add-icon' }))
vi.mock('@/assets/svg/de-copy.svg', () => ({ default: 'copy-icon' }))
vi.mock('@/assets/svg/de-delete.svg', () => ({ default: 'delete-icon' }))
vi.mock('@/assets/svg/icon_warning_filled.svg', () => ({ default: 'warning-icon' }))
vi.mock('@/assets/svg/icon_delete-trash_outlined.svg', () => ({ default: 'trash-icon' }))
vi.mock('@/assets/svg/icon_edit_outlined.svg', () => ({ default: 'edit-icon' }))

import EditorDetail from '../EditorDetail.vue'

const globalStubs = {
  'el-form': { template: '<form><slot /></form>' },
  'el-form-item': { template: '<div><slot /></div>' },
  'el-input': { template: '<input />' },
  'el-select': { template: '<select><slot /></select>' },
  'el-option': { template: '<option />' },
  'el-button': { template: '<button><slot /></button>' },
  'el-dialog': { template: '<div class="el-dialog"><slot /></div>' },
  'el-table': { template: '<table><slot /></table>' },
  'el-table-column': { template: '<td><slot /></td>' },
  'el-icon': { template: '<i><slot /></i>' },
  'el-tooltip': { template: '<span><slot /></span>' },
  'el-popover': { template: '<div><slot /></div>' },
  'el-checkbox': { template: '<input type="checkbox" />' },
  'el-switch': { template: '<button />' },
  'el-radio': { template: '<input type="radio" />' },
  'el-radio-group': { template: '<div><slot /></div>' },
  'el-tag': { template: '<span><slot /></span>' },
  'el-dropdown': { template: '<div><slot /></div>' },
  'el-dropdown-menu': { template: '<div><slot /></div>' },
  'el-dropdown-item': { template: '<div><slot /></div>' },
  'el-collapse': { template: '<div><slot /></div>' },
  'el-collapse-item': { template: '<div><slot /></div>' }
}

describe('EditorDetail', () => {
  const mountComponent = () =>
    shallowMount(EditorDetail, {
      props: {
        form: {
          id: 0,
          name: '',
          desc: '',
          type: 'API',
          apiConfiguration: []
        },
        activeStep: 1
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
