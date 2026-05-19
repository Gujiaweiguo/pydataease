import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: [] })),
    post: vi.fn(() => Promise.resolve({ data: {} }))
  }
}))

vi.mock('element-plus-secondary', () => ({
  ElMessage: { success: vi.fn(), error: vi.fn() },
  ElLoading: { service: vi.fn(() => ({ close: vi.fn() })) }
}))

import BasicEdit from '../BasicEdit.vue'

const globalStubs = {
  ElDrawer: {
    template: '<div v-if="modelValue"><slot /><slot name="footer" /></div>',
    props: ['modelValue', 'title', 'size', 'direction', 'modalClass']
  },
  ElForm: {
    template: '<form><slot /></form>',
    props: ['model', 'rules', 'labelWidth', 'labelPosition', 'requireAsteriskPosition'],
    methods: { validate: vi.fn((cb: any) => cb(true)), resetFields: vi.fn() }
  },
  ElFormItem: {
    template: '<div><slot /><slot name="label" /></div>',
    props: ['label', 'prop', 'class']
  },
  ElSwitch: { template: '<div />', props: ['modelValue', 'activeValue', 'inactiveValue'] },
  ElInputNumber: {
    template: '<input type="number" />',
    props: ['modelValue', 'min', 'max', 'step', 'placeholder', 'controlsPosition']
  },
  ElSelect: { template: '<select><slot /></select>', props: ['modelValue'] },
  ElOption: { template: '<option />', props: ['label', 'value', 'key'] },
  ElTreeSelect: { template: '<div />', props: ['modelValue', 'data'] },
  ElRadioGroup: { template: '<div><slot /></div>', props: ['modelValue'] },
  ElRadio: { template: '<label><slot /></label>', props: ['label'] },
  ElButton: { template: '<button><slot /></button>' },
  ElTooltip: { template: '<div><slot /></div>' },
  ElIcon: { template: '<i><slot /></i>' },
  Icon: { template: '<i><slot /></i>' }
}

describe('BasicEdit', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(BasicEdit, {
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('exposes edit method', () => {
    const wrapper = shallowMount(BasicEdit, {
      global: { stubs: globalStubs }
    })
    expect(typeof (wrapper.vm as any).edit).toBe('function')
  })

  it('has validation rules for dsIntervalTime', () => {
    const wrapper = shallowMount(BasicEdit, {
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.rule.dsIntervalTime).toBeDefined()
  })

  it('has default form state with dsIntervalTime 30', () => {
    const wrapper = shallowMount(BasicEdit, {
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.state.form.dsIntervalTime).toBe('30')
  })

  it('has options for time intervals', () => {
    const wrapper = shallowMount(BasicEdit, {
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.options.length).toBe(2)
  })
})
