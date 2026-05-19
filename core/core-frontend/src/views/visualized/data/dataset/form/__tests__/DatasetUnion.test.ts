import { defineComponent } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('@/utils/color', () => ({
  getCSSVariable: () => '#3370ff'
}))

vi.mock('@/api/dataset', () => ({
  getTableField: vi.fn()
}))

vi.mock('@/components/handle-more', () => ({
  HandleMore: { template: '<div><slot /></div>' }
}))

vi.mock('@/store/modules/appearance', () => ({
  useAppearanceStoreWithOut: () => ({ themeColor: 'default', customColor: '' })
}))

vi.mock('../AddSql.vue', () => ({
  default: { template: '<div class="add-sql-stub" />' }
}))

import DatasetUnion from '../DatasetUnion.vue'

const globalStubs = {
  AddSql: { template: '<div class="add-sql-stub" />' },
  UnionFieldList: { template: '<div class="union-field-list-stub" />' },
  HandleMore: { template: '<div class="handle-more-stub" />' },
  ElDialog: defineComponent({
    name: 'ElDialog',
    props: ['modelValue'],
    template: '<div v-if="modelValue"><slot /><slot name="footer" /></div>'
  }),
  ElDrawer: defineComponent({
    name: 'ElDrawer',
    props: ['modelValue'],
    template: '<div v-if="modelValue"><slot /><slot name="header" /><slot name="footer" /></div>'
  }),
  ElButton: { template: '<button><slot /></button>' },
  ElInput: { template: '<input />', props: ['modelValue'] },
  ElForm: { template: '<form><slot /></form>' },
  ElFormItem: { template: '<div><slot /></div>' },
  ElIcon: { template: '<i><slot /></i>' },
  Icon: { template: '<span><slot /></span>' }
}

const provideDefaults = () => ({
  isCross: { value: false },
  allfields: { value: [] }
})

describe('DatasetUnion', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(DatasetUnion, {
      props: { maskShow: false, offsetX: 0, offsetY: 0, dragHeight: 260 },
      global: { stubs: globalStubs, provide: provideDefaults() }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('exposes initState method', () => {
    const wrapper = shallowMount(DatasetUnion, {
      props: { maskShow: false, offsetX: 0, offsetY: 0, dragHeight: 260 },
      global: { stubs: globalStubs, provide: provideDefaults() }
    })
    expect(typeof (wrapper.vm as any).initState).toBe('function')
  })

  it('exposes getNodeList method', () => {
    const wrapper = shallowMount(DatasetUnion, {
      props: { maskShow: false, offsetX: 0, offsetY: 0, dragHeight: 260 },
      global: { stubs: globalStubs, provide: provideDefaults() }
    })
    expect(typeof (wrapper.vm as any).getNodeList).toBe('function')
  })

  it('exposes setStateBack method', () => {
    const wrapper = shallowMount(DatasetUnion, {
      props: { maskShow: false, offsetX: 0, offsetY: 0, dragHeight: 260 },
      global: { stubs: globalStubs, provide: provideDefaults() }
    })
    expect(typeof (wrapper.vm as any).setStateBack).toBe('function')
  })
})
