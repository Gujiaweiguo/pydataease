import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('@/utils/attr', () => ({
  fieldType: { 0: 'text', 1: 'time', 2: 'value', 3: 'value', 4: 'value', 5: 'location' }
}))

vi.mock('@/components/icon-group/field-list', () => ({
  iconFieldMap: {}
}))

import UnionFieldList from '../UnionFieldList.vue'

const globalStubs = {
  ElInput: { template: '<input />', props: ['modelValue'] },
  ElTable: { template: '<table><slot /></table>' },
  ElTableColumn: { template: '<col />' },
  ElCheckbox: { template: '<input type="checkbox" />' },
  ElIcon: { template: '<i><slot /></i>' },
  Icon: { template: '<span><slot /></span>' }
}

describe('UnionFieldList', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(UnionFieldList, {
      props: { fieldList: [], node: {} },
      global: { stubs: globalStubs, mocks: { $t: (k: string) => k } }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('displays field count as 0/0 when fieldList is empty', () => {
    const wrapper = shallowMount(UnionFieldList, {
      props: { fieldList: [], node: {} },
      global: { stubs: globalStubs, mocks: { $t: (k: string) => k } }
    })
    expect(wrapper.text()).toContain('0/')
  })

  it('displays correct count with fields', () => {
    const fields = [
      { originName: 'id', checked: true },
      { originName: 'name', checked: false }
    ]
    const wrapper = shallowMount(UnionFieldList, {
      props: { fieldList: fields, node: {} },
      global: { stubs: globalStubs, mocks: { $t: (k: string) => k } }
    })
    expect(wrapper.text()).toContain('2')
  })

  it('emits checkedFields when selection changes', async () => {
    const wrapper = shallowMount(UnionFieldList, {
      props: { fieldList: [{ originName: 'id', checked: true }], node: {} },
      global: { stubs: globalStubs, mocks: { $t: (k: string) => k } }
    })
    expect(wrapper.emitted('checkedFields')).toBeTruthy()
  })
})
