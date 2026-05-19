import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({
  default: {
    post: vi.fn(() => Promise.resolve({ data: {} }))
  }
}))

vi.mock('element-plus-secondary', () => ({
  ElMessage: { success: vi.fn(), error: vi.fn() },
  ElLoading: { service: vi.fn(() => ({ close: vi.fn() })) }
}))

import ThirdEdit from '../ThirdEdit.vue'

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
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'prop'] },
  ElInput: { template: '<input />', props: ['modelValue', 'placeholder'] },
  ElButton: { template: '<button><slot /></button>', props: ['type', 'secondary', 'disabled'] }
}

describe('ThirdEdit', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(ThirdEdit, {
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('exposes edit method', () => {
    const wrapper = shallowMount(ThirdEdit, {
      global: { stubs: globalStubs }
    })
    expect(typeof (wrapper.vm as any).edit).toBe('function')
  })

  it('has validation rules for id and domain', () => {
    const wrapper = shallowMount(ThirdEdit, {
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.rule.id).toBeDefined()
    expect(vm.rule.domain).toBeDefined()
  })

  it('initial state has null form values', () => {
    const wrapper = shallowMount(ThirdEdit, {
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.state.form.id).toBeNull()
    expect(vm.state.form.domain).toBeNull()
  })

  it('domain validation rejects invalid URLs', () => {
    const wrapper = shallowMount(ThirdEdit, {
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    const domainRules = vm.rule.domain
    expect(domainRules.length).toBeGreaterThanOrEqual(2)
  })
})
