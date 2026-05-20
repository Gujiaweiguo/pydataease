import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/api/dataset', () => ({
  getFunction: vi.fn(() => Promise.resolve([]))
}))
vi.mock('@/utils/attr', () => ({
  fieldType: { 0: 'text', 1: 'time', 2: 'value', 3: 'value', 4: 'value', 5: 'text' }
}))
vi.mock('@/components/icon-group/field-list', () => ({
  iconFieldMap: {}
}))

const mockCodeComInit = vi.fn(() => ({
  dispatch: vi.fn(),
  state: { doc: { toString: () => '' }, selection: { ranges: [{ from: 0 }] } },
  viewState: { state: { doc: { length: 0 }, selection: { ranges: [{ from: 0 }] } } },
  destroy: vi.fn()
}))

import CustomAggrEdit from '../CustomAggrEdit.vue'

describe('CustomAggrEdit', () => {
  it('renders component', () => {
    const wrapper = shallowMount(CustomAggrEdit, {
      props: { crossDs: false },
      global: {
        stubs: {
          'el-input': true,
          'el-icon': { template: '<div><slot /></div>' },
          'el-tooltip': { template: '<div><slot /></div>' },
          'el-scrollbar': { template: '<div><slot /></div>' },
          'el-popover': { template: '<div><slot /><slot name="reference" /></div>' },
          'el-row': { template: '<div><slot /></div>' },
          Icon: { template: '<div><slot /></div>' },
          icon_info_outlined: true,
          icon_searchOutline_outlined: true,
          icon_adjustment_outlined: true,
          icon_edit_outlined: true,
          icon_deleteTrash_outlined: true,
          'code-mirror': {
            template: '<div class="code-mirror-stub"></div>',
            methods: {
              codeComInit: mockCodeComInit
            }
          }
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains calcu-field wrapper', () => {
    const wrapper = shallowMount(CustomAggrEdit, {
      props: { crossDs: false },
      global: {
        stubs: {
          'el-input': true,
          'el-icon': { template: '<div><slot /></div>' },
          'el-tooltip': { template: '<div><slot /></div>' },
          'el-scrollbar': { template: '<div><slot /></div>' },
          'el-popover': { template: '<div><slot /><slot name="reference" /></div>' },
          'el-row': { template: '<div><slot /></div>' },
          Icon: { template: '<div><slot /></div>' },
          icon_info_outlined: true,
          icon_searchOutline_outlined: true,
          icon_adjustment_outlined: true,
          icon_edit_outlined: true,
          icon_deleteTrash_outlined: true,
          'code-mirror': {
            template: '<div class="code-mirror-stub"></div>',
            methods: {
              codeComInit: mockCodeComInit
            }
          }
        }
      }
    })
    expect(wrapper.find('.calcu-field').exists()).toBe(true)
  })
})
