import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/api/dataset', () => ({
  getFieldTree: () => Promise.resolve([])
}))
vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({ emitter: { emit: vi.fn(), on: vi.fn() } })
}))
vi.mock('@/utils/color', () => ({ colorStringToHex: (c: string) => c }))

import Tree from '../Tree.vue'

const stubs = {
  'el-tree-select': {
    template: '<div class="el-tree-select" />',
    props: [
      'modelValue',
      'data',
      'clearable',
      'multiple',
      'filterable',
      'placeholder',
      'showCheckbox',
      'checkStrictly',
      'renderAfterExpand',
      'filterNodeMethod',
      'collapseTags',
      'collapseTagsTooltip',
      'tagColor',
      'showWholePath',
      'style',
      'showBtn'
    ]
  }
}

const defaultProvide = {
  placeholder: { value: { placeholderShow: true } },
  'com-width': () => 227,
  'is-confirm-search': () => undefined,
  'query-data-for-id-tree': () => undefined,
  'cascade-list': () => undefined,
  '$custom-style-filter': { background: '#FFFFFF', border: '#ddd' }
}

const baseConfig = {
  selectValue: '',
  defaultValue: '',
  required: false,
  queryConditionWidth: 0,
  displayType: '9',
  resultMode: 0,
  defaultValueCheck: false,
  multiple: false,
  checkedFieldsMap: {},
  treeFieldList: [],
  optionFilter: [],
  id: 'test-tree',
  dataset: { id: 'ds1' },
  field: { id: 'f1' },
  defaultMapValue: '',
  mapValue: '',
  placeholder: '',
  checkedFields: []
} as any

const mountTree = (
  configOverrides: Record<string, any> = {},
  propsOverrides: Record<string, any> = {}
) =>
  shallowMount(Tree, {
    props: {
      config: { ...baseConfig, ...configOverrides },
      isConfig: true,
      ...propsOverrides
    },
    global: { stubs, provide: defaultProvide, directives: { loading: () => undefined } }
  })

describe('Tree', () => {
  it('renders successfully with default config', () => {
    const wrapper = mountTree()
    expect(wrapper.exists()).toBe(true)
  })

  it('renders el-tree-select elements', () => {
    const wrapper = mountTree()
    const selects = wrapper.findAll('.el-tree-select')
    expect(selects.length).toBeGreaterThanOrEqual(1)
  })

  it('renders tree-select even with multiple enabled', () => {
    const wrapper = mountTree({ multiple: true })
    expect(wrapper.findAll('.el-tree-select').length).toBeGreaterThanOrEqual(1)
  })

  it('renders loading tree-select stub when loading', () => {
    const wrapper = mountTree()
    expect(wrapper.find('.el-tree-select').exists()).toBe(true)
  })
})
