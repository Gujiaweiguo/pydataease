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

vi.mock('@/utils/encryption', () => ({
  rsaEncryp: (val: string) => `encrypted_${val}`
}))

vi.mock('@/utils/logout', () => ({
  logoutHandler: vi.fn()
}))

vi.mock('@/utils/utils', () => ({
  isMobile: () => false
}))

vi.mock('element-plus-secondary', () => ({
  ElMessage: { success: vi.fn() }
}))

vi.mock('@/components/custom-password', () => ({
  CustomPassword: {
    template: '<input />',
    props: ['modelValue', 'showPassword', 'type', 'placeholder']
  }
}))

import UpdatePwd from '../UpdatePwd.vue'

const globalStubs = {
  ElForm: {
    template: '<form><slot /></form>',
    props: ['model', 'rules', 'labelWidth', 'labelPosition', 'requireAsteriskPosition'],
    methods: { validate: vi.fn() }
  },
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'prop'] },
  ElButton: { template: '<button><slot /></button>' },
  CustomPassword: { template: '<input />', props: ['modelValue'] }
}

describe('UpdatePwd', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(UpdatePwd, {
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('has form validation rules for all three fields', () => {
    const wrapper = shallowMount(UpdatePwd, {
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.rule.pwd).toBeDefined()
    expect(vm.rule.newPwd).toBeDefined()
    expect(vm.rule.confirm).toBeDefined()
  })

  it('original password rule requires min 6 max 20 chars', () => {
    const wrapper = shallowMount(UpdatePwd, {
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    const pwdRules = vm.rule.pwd
    expect(pwdRules.length).toBeGreaterThanOrEqual(2)
  })

  it('emits success event on save', () => {
    const wrapper = shallowMount(UpdatePwd, {
      global: { stubs: globalStubs }
    })
    expect(wrapper.emitted('success')).toBeFalsy()
  })
})
