import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/store', () => ({ store: {} }))

vi.mock('pinia', () => ({
  defineStore: vi.fn(),
  storeToRefs: vi.fn(() => ({})),
  createPinia: vi.fn()
}))

vi.mock('@/utils/attr', () => ({
  fieldType: { 0: 'text', 2: 'value' }
}))

vi.mock('@/components/icon-group/field-list', () => ({
  iconFieldMap: { text: 'field-text', value: 'field-value' }
}))

vi.mock('vuedraggable', () => ({
  default: { template: '<div><slot /></div>', props: ['list', 'group', 'itemKey'] }
}))

vi.mock('@/assets/svg/icon_view-list_outlined.svg', () => ({ default: { template: '<svg />' } }))
vi.mock('@/assets/svg/icon_expand-right_filled.svg', () => ({ default: { template: '<svg />' } }))

import FilterConfigIndex from '@/views/visualized/view/panel/filter-config/index.vue'

const stubs = {
  ElSelectV2: {
    template: '<div />',
    props: [
      'modelValue',
      'filterable',
      'popperClass',
      'showChecked',
      'multiple',
      'collapseTags',
      'options',
      'collapseTagsTooltip',
      'placeholder',
      'style'
    ]
  },
  ElRadioGroup: { template: '<div><slot /></div>', props: ['modelValue'] },
  ElRadio: { template: '<label><slot /></label>', props: ['label'] },
  ElTabs: { template: '<div><slot /></div>', props: ['modelValue'] },
  ElTabPane: { template: '<div><slot /></div>', props: ['label', 'name'] },
  ElTreeSelect: { template: '<select />', props: ['modelValue', 'data', 'renderAfterExpand'] },
  ElSelect: {
    template: '<select><slot /></select>',
    props: ['modelValue', 'filterable', 'multiple']
  },
  ElOption: { template: '<option><slot /></option>', props: ['label', 'value'] },
  ElIcon: { template: '<i><slot /></i>' },
  Icon: { template: '<span><slot /></span>', props: ['name'] },
  ElCheckbox: { template: '<input type="checkbox" />', props: ['modelValue'] },
  ElInput: { template: '<input />', props: ['modelValue'] },
  ElColorPicker: { template: '<div />', props: ['modelValue', 'showAlpha'] },
  ElInputNumber: {
    template: '<input type="number" />',
    props: ['modelValue', 'min', 'max', 'size', 'controlsPosition']
  },
  FilterHead: { template: '<div />', props: ['dragItems'] },
  draggable: { template: '<div><slot /></div>', props: ['list', 'group', 'itemKey'] }
}

describe('FilterConfig index', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders successfully', () => {
    const wrapper = shallowMount(FilterConfigIndex, { global: { stubs } })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders multiple elements', () => {
    const wrapper = shallowMount(FilterConfigIndex, { global: { stubs } })
    expect(wrapper.element.children.length).toBeGreaterThan(0)
  })
})
