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

import Day from '../Day.vue'

const mountComponent = (props = {}) =>
  shallowMount(Day, {
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

describe('cron/Day', () => {
  it('renders the root container', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('div').exists()).toBe(true)
  })

  it('accepts modelValue prop', () => {
    const wrapper = mountComponent({ modelValue: '1' })
    expect(wrapper.props('modelValue')).toBe('1')
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
    const wrapper = mountComponent({ modelValue: '1-15' })
    const vm = wrapper.vm as any
    expect(vm.type).toBe('2')
    expect(vm.state.cycle.start).toBe(1)
    expect(vm.state.cycle.end).toBe(15)
  })

  it('parses step expression correctly', () => {
    const wrapper = mountComponent({ modelValue: '1/5' })
    const vm = wrapper.vm as any
    expect(vm.type).toBe('3')
    expect(vm.state.loop.start).toBe(1)
    expect(vm.state.loop.end).toBe(5)
  })

  it('parses last day expression L', () => {
    const wrapper = mountComponent({ modelValue: 'L' })
    const vm = wrapper.vm as any
    expect(vm.type).toBe('6')
  })

  it('parses work day expression W', () => {
    const wrapper = mountComponent({ modelValue: '15W' })
    const vm = wrapper.vm as any
    expect(vm.type).toBe('8')
    expect(vm.work).toBe(15)
  })

  it('parses specified week expression #', () => {
    const wrapper = mountComponent({ modelValue: '1#3' })
    const vm = wrapper.vm as any
    expect(vm.type).toBe('7')
    expect(vm.state.week.start).toBe(1)
    expect(vm.state.week.end).toBe(3)
  })

  it('parses comma-separated values', () => {
    const wrapper = mountComponent({ modelValue: '1,5,10' })
    const vm = wrapper.vm as any
    expect(vm.type).toBe('4')
    expect(vm.state.appoint).toEqual(['1', '5', '10'])
  })
})
