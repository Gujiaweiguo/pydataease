import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))

import DeInputNum from '../DeInputNum.vue'

const globalStubs = {
  'el-input-number': {
    template: '<input type="number" class="de-input-number" />',
    props: ['modelValue', 'effect', 'disabled', 'min', 'max', 'step', 'size', 'controlsPosition']
  }
}

describe('DeInputNum', () => {
  it('renders with default props', () => {
    const wrapper = shallowMount(DeInputNum, { global: { stubs: globalStubs } })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('input[type="number"]').exists()).toBe(true)
  })

  it('applies light theme class by default', () => {
    const wrapper = shallowMount(DeInputNum, { global: { stubs: globalStubs } })
    expect(wrapper.find('.de-input-number').exists()).toBe(true)
    expect(wrapper.find('.light-custom-input-number').exists()).toBe(true)
  })

  it('applies dark theme class when themes prop is dark', () => {
    const wrapper = shallowMount(DeInputNum, {
      props: { themes: 'dark' },
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.dark-custom-input-number').exists()).toBe(true)
  })

  it('passes min, max, step, and disabled props to el-input-number', () => {
    const wrapper = shallowMount(DeInputNum, {
      props: { min: 0, max: 100, step: 5, disabled: true },
      global: { stubs: globalStubs }
    })
    const stub = wrapper.findComponent(globalStubs['el-input-number'] as any)
    expect(stub.props('min')).toBe(0)
    expect(stub.props('max')).toBe(100)
    expect(stub.props('step')).toBe(5)
    expect(stub.props('disabled')).toBe(true)
  })

  it('passes value as modelValue', () => {
    const wrapper = shallowMount(DeInputNum, {
      props: { value: 42 },
      global: { stubs: globalStubs }
    })
    const stub = wrapper.findComponent(globalStubs['el-input-number'] as any)
    expect(stub.props('modelValue')).toBe(42)
  })
})
