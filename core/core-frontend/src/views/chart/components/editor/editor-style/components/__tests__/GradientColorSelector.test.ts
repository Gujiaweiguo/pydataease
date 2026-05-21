import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_CASES: [
    { name: 'Default', value: 'default', colors: ['#3370ff', '#04b49c', '#5470c6'] },
    { name: 'Custom', value: 'custom', colors: ['#ff0000', '#00ff00', '#0000ff'] }
  ]
}))
vi.mock('@/views/chart/components/js/util', () => ({
  getMapColorCases: (cases: any[]) => cases.map(c => ({ ...c, value: c.value + '_split_gradient' }))
}))
vi.mock('element-plus-secondary', () => ({
  ElPopover: {
    template: '<div><slot /></div>',
    props: [
      'placement',
      'width',
      'trigger',
      'persistent',
      'showArrow',
      'popperStyle',
      'effect',
      'offset'
    ]
  }
}))

import GradientColorSelector from '../GradientColorSelector.vue'

const globalStubs = {
  ElInput: { template: '<input />', props: ['effect', 'readonly', 'class'] },
  ElIcon: { template: '<i><slot /></i>', props: ['class'] },
  ElTabs: { template: '<div><slot /></div>', props: ['modelValue', 'class'] },
  ElTabPane: { template: '<div><slot /></div>', props: ['label', 'name', 'class'] },
  ElScrollbar: { template: '<div><slot /></div>', props: ['maxHeight', 'class'] },
  ArrowDown: { template: '<span>▼</span>' }
}

const defaultProps = () => ({
  modelValue: {
    basicStyleForm: {
      colors: ['#3370ff', '#04b49c', '#5470c6'],
      colorScheme: 'default'
    },
    customColor: null,
    colorIndex: 0
  },
  propertyInner: ['colors'],
  themes: 'light'
})

describe('GradientColorSelector', () => {
  it('renders with required props', () => {
    const wrapper = shallowMount(GradientColorSelector, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('initializes with simple tab by default', () => {
    const wrapper = shallowMount(GradientColorSelector, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.form.activeName).toBe('simple')
  })

  it('sets activeName to split_gradient for gradient color schemes', () => {
    const props = defaultProps()
    props.modelValue.basicStyleForm.colorScheme = 'default_split_gradient'
    const wrapper = shallowMount(GradientColorSelector, {
      props,
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.form.activeName).toBe('split_gradient')
  })

  it('emits selectColorCase when selectNode is called', async () => {
    const wrapper = shallowMount(GradientColorSelector, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    const option = { name: 'Custom', value: 'custom', colors: ['#ff0000', '#00ff00'] }
    vm.selectNode(option)
    const colorCaseEvents = wrapper.emitted('selectColorCase')
    expect(colorCaseEvents).toBeTruthy()
    expect(colorCaseEvents?.[0]?.[0]).toEqual(option)
  })

  it('computes state from modelValue', () => {
    const wrapper = shallowMount(GradientColorSelector, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.state.basicStyleForm.colors[0]).toBe('#3370ff')
  })
})
