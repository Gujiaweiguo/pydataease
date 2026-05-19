import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/api/template', () => ({
  batchUpdate: () => Promise.resolve(),
  findCategoriesByTemplateIds: () => Promise.resolve({ data: [] })
}))
vi.mock('element-plus-secondary', () => ({
  ElMessage: { warning: () => undefined, success: () => undefined }
}))

import DeCategoryChange from '../DeCategoryChange.vue'

const globalStubs = {
  ElForm: { template: '<form><slot /></form>', props: ['model', 'rules', 'labelPosition'] },
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'prop', 'style'] },
  ElSelect: { template: '<select><slot /></select>', props: ['modelValue', 'multiple', 'style', 'popperClass'] },
  ElOption: { template: '<option><slot /></option>', props: ['key', 'label', 'value'] },
  ElRow: { template: '<div><slot /></div>', props: ['class'] },
  ElButton: { template: '<button><slot /></button>', props: ['secondary', 'type'] }
}

const defaultProps = () => ({
  templateCategories: [
    { id: 'cat1', name: 'Category 1' },
    { id: 'cat2', name: 'Category 2' }
  ],
  templateIds: ['tmpl1', 'tmpl2']
})

describe('DeCategoryChange', () => {
  it('renders with required props', () => {
    const wrapper = shallowMount(DeCategoryChange, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('emits closeBatchEditTemplateDialog when cancel is called', () => {
    const wrapper = shallowMount(DeCategoryChange, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    vm.cancel()
    expect(wrapper.emitted('closeBatchEditTemplateDialog')).toBeTruthy()
  })

  it('has templateInfoRules with categories required validation', () => {
    const wrapper = shallowMount(DeCategoryChange, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.state.templateInfoRules.categories).toBeDefined()
    expect(vm.state.templateInfoRules.categories[0].required).toBe(true)
  })

  it('saveChange returns false when categories is empty', () => {
    const wrapper = shallowMount(DeCategoryChange, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    vm.state.templateInfo.categories = []
    const result = vm.saveChange()
    expect(result).toBe(false)
  })
})
