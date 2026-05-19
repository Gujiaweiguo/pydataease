import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))

import NumberInput from '../NumberInput.vue'

const stubs = {
  'el-input-number': {
    template: '<input type="number" class="el-input-number-stub" />',
    props: ['modelValue', 'placeholder', 'controlsPosition', 'style']
  }
}

const defaultProvide = {
  placeholder: { value: { placeholderShow: true } },
  'com-width': () => 227,
  'is-confirm-search': () => undefined,
  '$custom-style-filter': { background: '#fff', border: '#ccc' }
}

const baseConfig = {
  id: 'test-num',
  queryConditionWidth: 0,
  defaultNumValueEnd: 100,
  defaultNumValueStart: 0,
  numValueEnd: 100,
  numValueStart: 0,
  defaultValueCheck: true,
  placeholder: 'Enter number'
}

const mountNumberInput = (configOverrides: Record<string, any> = {}, propsOverrides: Record<string, any> = {}) =>
  shallowMount(NumberInput, {
    props: {
      config: { ...baseConfig, ...configOverrides },
      isConfig: false,
      ...propsOverrides
    },
    global: { stubs, provide: defaultProvide }
  })

describe('NumberInput', () => {
  it('renders successfully with default props', () => {
    const wrapper = mountNumberInput()
    expect(wrapper.exists()).toBe(true)
  })

  it('renders two input-number stubs for start and end range', () => {
    const wrapper = mountNumberInput()
    const inputs = wrapper.findAll('.el-input-number-stub')
    expect(inputs.length).toBe(2)
  })

  it('has the num-search-select wrapper div', () => {
    const wrapper = mountNumberInput()
    expect(wrapper.find('.num-search-select').exists()).toBe(true)
  })

  it('does not set default values when defaultValueCheck is false', () => {
    const wrapper = mountNumberInput({ defaultValueCheck: false })
    expect(wrapper.exists()).toBe(true)
    expect((wrapper.vm as any).config.numValueStart).toBeUndefined()
  })
})
