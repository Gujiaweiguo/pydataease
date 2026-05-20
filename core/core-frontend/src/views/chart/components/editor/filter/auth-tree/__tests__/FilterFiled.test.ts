import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/api/dataset', () => ({
  multFieldValuesForPermissions: vi.fn(() => Promise.resolve({ data: [] }))
}))

import FilterFiled from '../FilterFiled.vue'

describe('FilterFiled (auth-tree)', () => {
  const defaultItem = {
    term: '',
    fieldId: '',
    filterType: '',
    timeType: 'year',
    deType: 0,
    enumValue: [],
    name: '',
    value: null,
    timeValue: ''
  }

  const defaultStubs = {
    'el-dropdown': { template: '<div><slot /><slot name="dropdown" /></div>' },
    'el-dropdown-menu': { template: '<div><slot /></div>' },
    'el-input': true,
    'el-select': true,
    'el-option': true,
    'el-icon': { template: '<div><slot /></div>' },
    'el-popover': { template: '<div><slot /><slot name="reference" /></div>' },
    'el-checkbox': true,
    'el-checkbox-group': { template: '<div><slot /></div>' },
    'el-scrollbar': { template: '<div><slot /></div>' },
    'el-button': true,
    'el-input-number': true,
    'el-tooltip': { template: '<div><slot /></div>' },
    'time-set-dialog': true,
    Icon: { template: '<div><slot /></div>' },
    icon_searchOutline_outlined: true,
    icon_close_outlined: true,
    icon_deleteTrash_outlined: true
  }

  it('renders component', () => {
    const wrapper = shallowMount(FilterFiled, {
      props: { index: 0, item: defaultItem },
      global: {
        provide: {
          getAuthTargetType: { authTargetType: '' },
          filedList: { value: {} }
        },
        stubs: defaultStubs
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains white-nowrap wrapper', () => {
    const wrapper = shallowMount(FilterFiled, {
      props: { index: 0, item: defaultItem },
      global: {
        provide: {
          getAuthTargetType: { authTargetType: '' },
          filedList: { value: {} }
        },
        stubs: defaultStubs
      }
    })
    expect(wrapper.find('.white-nowrap').exists()).toBe(true)
  })
})
