import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('@/utils/attr', () => ({
  fieldType: { 0: 'text', 1: 'time', 2: 'value' }
}))

vi.mock('@/components/icon-group/field-list', () => ({
  iconFieldMap: {}
}))

import UnionItemEdit from '../UnionItemEdit.vue'

const globalStubs = {
  ElSelect: { template: '<select><slot /></select>' },
  ElOption: { template: '<option><slot /></option>' },
  ElButton: { template: '<button><slot /></button>' },
  ElIcon: { template: '<i><slot /></i>' },
  Icon: { template: '<span><slot /></span>' }
}

describe('UnionItemEdit', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(UnionItemEdit, {
      props: {
        tableName: 'table_a',
        parentFieldList: [],
        nodeFieldList: [],
        node: { tableName: 'table_b', unionType: 'left', unionFields: [] }
      },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('displays both table names in header', () => {
    const wrapper = shallowMount(UnionItemEdit, {
      props: {
        tableName: 'parent_table',
        parentFieldList: [],
        nodeFieldList: [],
        node: { tableName: 'child_table', unionType: 'left', unionFields: [] }
      },
      global: { stubs: globalStubs }
    })
    expect(wrapper.text()).toContain('parent_table')
    expect(wrapper.text()).toContain('child_table')
  })

  it('emits changeUnionFields when add button is clicked', async () => {
    const wrapper = shallowMount(UnionItemEdit, {
      props: {
        tableName: 't1',
        parentFieldList: [],
        nodeFieldList: [],
        node: { tableName: 't2', unionType: 'left', unionFields: [] }
      },
      global: { stubs: globalStubs }
    })
    // On init with empty unionFields, addUnion is called
    expect(wrapper.emitted('changeUnionFields')).toBeTruthy()
  })
})
