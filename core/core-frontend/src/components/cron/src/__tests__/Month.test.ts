import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/utils/propTypes', () => ({
  propTypes: {
    string: { def: (v: string) => v }
  }
}))

import Month from '../Month.vue'

const mountComponent = (props = {}) =>
  shallowMount(Month, {
    props: {
      modelValue: '*',
      ...props
    },
    global: {
      stubs: {
        'el-radio': { template: '<label><slot /></label>' },
        'el-input-number': { template: '<div class="el-input-number" />' },
        'el-checkbox-group': { template: '<div><slot /></div>' },
        'el-checkbox': { template: '<label><slot /></label>' }
      }
    }
  })

describe('cron/Month', () => {
  it('renders the root container', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('div').exists()).toBe(true)
  })

  it('accepts modelValue prop', () => {
    const wrapper = mountComponent({ modelValue: '6' })
    expect(wrapper.props('modelValue')).toBe('6')
  })

  it('defaults to wildcard when modelValue is *', () => {
    const wrapper = mountComponent({ modelValue: '*' })
    const vm = wrapper.vm as any
    expect(vm.type).toBe('1')
  })

  it('parses unspecified expression ?', () => {
    const wrapper = mountComponent({ modelValue: '?' })
    const vm = wrapper.vm as any
    expect(vm.type).toBe('5')
  })

  it('parses range expression correctly', () => {
    const wrapper = mountComponent({ modelValue: '1-6' })
    const vm = wrapper.vm as any
    expect(vm.type).toBe('2')
    expect(vm.state.cycle.start).toBe('1')
    expect(vm.state.cycle.end).toBe('6')
  })

  it('parses step expression correctly', () => {
    const wrapper = mountComponent({ modelValue: '1/2' })
    const vm = wrapper.vm as any
    expect(vm.type).toBe('3')
    expect(vm.state.loop.start).toBe('1')
    expect(vm.state.loop.end).toBe('2')
  })

  it('computes resultValue as wildcard for type 1', () => {
    const wrapper = mountComponent({ modelValue: '*' })
    const vm = wrapper.vm as any
    expect(vm.resultValue).toBe('*')
  })
})
