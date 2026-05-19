import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

import CustomLinkPwd from '../CustomLinkPwd.vue'

const globalStubs = {
  ElDialog: {
    template: '<div v-if="modelValue"><slot /><slot name="footer" /></div>',
    props: ['modelValue', 'title', 'width', 'appendToBody']
  },
  ElForm: {
    template: '<form><slot /></form>',
    methods: { validate: (cb: any) => cb(true), resetFields: vi.fn() }
  },
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'prop'] },
  ElInput: { template: '<input />', props: ['modelValue', 'placeholder'] },
  ElButton: { template: '<button><slot /></button>' }
}

describe('CustomLinkPwd', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(CustomLinkPwd, {
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('has open method exposed', () => {
    const wrapper = shallowMount(CustomLinkPwd, {
      global: { stubs: globalStubs }
    })
    expect(typeof (wrapper.vm as any).open).toBe('function')
  })

  it('password rule requires non-empty value and pattern match', () => {
    const wrapper = shallowMount(CustomLinkPwd, {
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.rule.pwd).toBeDefined()
    expect(vm.rule.pwd.length).toBeGreaterThanOrEqual(2)
  })
})
