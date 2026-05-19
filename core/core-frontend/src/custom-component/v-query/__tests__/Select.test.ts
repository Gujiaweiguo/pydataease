import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    dvInfo: { type: 'dashboard' },
    mobileInPc: false
  })
}))
vi.mock('@/api/dataset', () => ({
  enumValueObj: () => Promise.resolve([]),
  getEnumValue: () => Promise.resolve([])
}))
vi.mock('@/utils/eventBus', () => ({
  default: { on: vi.fn(), off: vi.fn(), emit: vi.fn() }
}))
vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({ emitter: { emit: vi.fn(), on: vi.fn() } })
}))
vi.mock('@/utils/color', () => ({ colorStringToHex: (c: string) => c }))
vi.mock('@/utils/utils', () => ({ isMobile: () => false }))

import Select from '../Select.vue'

const stubs = {
  'el-select-v2': {
    template: '<div class="el-select-v2" />',
    props: ['modelValue', 'placeholder', 'multiple', 'options', 'clearable', 'filterable']
  },
  Flat: { template: '<div class="flat-stub" />' },
  VanPopupSelect: { template: '<div class="van-popup-stub" />' }
}

const defaultProvide = {
  'unmount-select': { value: [] },
  placeholder: { value: { placeholderShow: true } },
  'release-unmount-select': () => undefined,
  'query-data-for-id': () => undefined,
  'is-confirm-search': () => undefined,
  'com-width': () => 227,
  'cascade-list': () => undefined,
  'set-cascade-default': () => undefined,
  '$custom-style-filter': { background: '#FFFFFF', border: '#ddd' }
}

const baseConfig = {
  selectValue: '',
  required: false,
  displayFormat: 0,
  queryConditionWidth: 0,
  resultMode: 0,
  defaultValue: '',
  displayType: '0',
  defaultValueCheck: false,
  optionValueSource: 0,
  multiple: false,
  checkedFieldsMap: {},
  optionFilter: [],
  id: 'test-select',
  showEmpty: false,
  field: { id: 'f1' },
  displayId: '',
  sort: '',
  sortId: '',
  checkedFields: [],
  valueSource: [],
  placeholder: 'Select...',
  name: 'Test'
}

const mountSelect = (configOverrides: Record<string, any> = {}, propsOverrides: Record<string, any> = {}) =>
  shallowMount(Select, {
    props: {
      config: { ...baseConfig, ...configOverrides },
      isConfig: true,
      ...propsOverrides
    },
    global: { stubs, provide: defaultProvide, directives: { loading: () => undefined } }
  })

describe('Select', () => {
  it('renders successfully with default config', () => {
    const wrapper = mountSelect()
    expect(wrapper.exists()).toBe(true)
  })

  it('shows el-select-v2 for non-flat display (displayFormat=0)', () => {
    const wrapper = mountSelect({ displayFormat: 0 })
    const select = wrapper.find('.el-select-v2')
    expect(select.exists()).toBe(true)
  })

  it('shows Flat component when displayFormat is 1', () => {
    const wrapper = mountSelect({ displayFormat: 1 })
    expect(wrapper.find('.flat-stub').exists()).toBe(true)
  })

  it('exposes displayTypeChange method', () => {
    const wrapper = mountSelect()
    expect(typeof (wrapper.vm as any).displayTypeChange).toBe('function')
  })
})
