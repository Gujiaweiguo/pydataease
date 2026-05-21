import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/api/template', () => ({
  save: () => Promise.resolve(),
  nameCheck: () => Promise.resolve({ data: 'not_exist' }),
  findOne: () => Promise.resolve({ data: { name: 'Test', snapshot: '', categories: [] } }),
  categoryTemplateNameCheck: () => Promise.resolve({ data: 'not_exist' })
}))
vi.mock('@/utils/imgUtils', () => ({
  imgUrlTrans: (url: string) => url
}))
vi.mock('element-plus-secondary', () => ({
  ElMessage: { warning: () => undefined, success: () => undefined },
  ElMessageBox: { confirm: () => Promise.resolve() }
}))

import DeTemplateImport from '../DeTemplateImport.vue'

const globalStubs = {
  ElForm: { template: '<form><slot /></form>', props: ['model', 'rules', 'labelPosition'] },
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'prop', 'style'] },
  ElInput: { template: '<input />', props: ['modelValue', 'placeholder', 'clearable'] },
  ElButton: { template: '<button><slot /></button>', props: ['style', 'icon', 'secondary'] },
  ElSelect: {
    template: '<select><slot /></select>',
    props: ['modelValue', 'multiple', 'style', 'popperClass']
  },
  ElOption: { template: '<option><slot /></option>', props: ['key', 'label', 'value'] },
  ElIcon: { template: '<i><slot /></i>' },
  ElRow: { template: '<div><slot /></div>', props: ['class'] },
  Plus: { template: '<span>+</span>' }
}

const defaultProps = () => ({
  pid: 'root',
  templateCategories: [{ id: 'cat1', name: 'Category 1' }],
  optType: 'insert'
})

describe('DeTemplateImport', () => {
  it('renders with required props', () => {
    const wrapper = shallowMount(DeTemplateImport, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('emits closeEditTemplateDialog when cancel is called', () => {
    const wrapper = shallowMount(DeTemplateImport, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    vm.cancel()
    expect(wrapper.emitted('closeEditTemplateDialog')).toBeTruthy()
  })

  it('saveTemplate returns false when name is empty', () => {
    const wrapper = shallowMount(DeTemplateImport, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    vm.state.templateInfo.name = ''
    const result = vm.saveTemplate()
    expect(result).toBe(false)
  })

  it('saveTemplate returns false when templateData is empty', () => {
    const wrapper = shallowMount(DeTemplateImport, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    vm.state.templateInfo.name = 'Test'
    vm.state.templateInfo.templateData = null
    const result = vm.saveTemplate()
    expect(result).toBe(false)
  })

  it('doAddCategory emits refresh with addCategory optType', () => {
    const wrapper = shallowMount(DeTemplateImport, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    vm.doAddCategory()
    const refreshEvents = wrapper.emitted('refresh')
    expect(refreshEvents).toBeTruthy()
    expect((refreshEvents?.[0]?.[0] as any).optType).toBe('addCategory')
  })

  it('classBackground returns empty object when no snapshot', () => {
    const wrapper = shallowMount(DeTemplateImport, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.classBackground).toEqual({})
  })
})
