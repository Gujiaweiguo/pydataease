import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#000', '#fff', '#ff0000', '#00ff00'],
  DEFAULT_COLOR_CASE: {
    color: {
      value: 'default',
      colors: ['#3370ff', '#04b49c', '#5470c6'],
      alpha: 100
    }
  },
  COLOR_CASES: [
    { name: 'Default', value: 'default', colors: ['#3370ff', '#04b49c', '#5470c6'] },
    { name: 'Custom', value: 'custom', colors: ['#ff0000', '#00ff00', '#0000ff'] }
  ]
}))

import ColorSelector from '../ColorSelector.vue'

const globalStubs = {
  ElForm: { template: '<form><slot /></form>', props: ['model', 'size'] },
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'class'] },
  ElSelect: { template: '<select><slot /></select>', props: ['modelValue', 'placeholder', 'size'] },
  ElOption: { template: '<option><slot /></option>', props: ['key', 'label', 'value'] },
  ElPopover: { template: '<div><slot /></div>', props: ['placement', 'width', 'trigger'] },
  ElButton: { template: '<button><slot /></button>', props: ['size', 'type'] },
  ElRadioGroup: { template: '<div><slot /></div>', props: ['modelValue', 'class'] },
  ElRadio: { template: '<label><slot /></label>', props: ['value', 'style'] },
  ElColorPicker: { template: '<div />', props: ['modelValue', 'predefine'] },
  ElInputNumber: {
    template: '<input type="number" />',
    props: ['modelValue', 'effect', 'min', 'max', 'size', 'controlsPosition']
  }
}

const defaultProps = () => ({
  chart: {
    customAttr: JSON.stringify({
      color: {
        value: 'default',
        colors: ['#3370ff', '#04b49c', '#5470c6'],
        alpha: 100
      }
    })
  },
  themes: 'dark'
})

describe('ColorSelector', () => {
  it('renders with required props', () => {
    const wrapper = shallowMount(ColorSelector, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('initializes colorForm from chart customAttr', () => {
    const wrapper = shallowMount(ColorSelector, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.state.colorForm.value).toBe('default')
    expect(vm.state.colorForm.alpha).toBe(100)
  })

  it('emits onColorChange when changeColorCase is called', () => {
    const wrapper = shallowMount(ColorSelector, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    vm.changeColorCase()
    expect(wrapper.emitted('onColorChange')).toBeTruthy()
  })

  it('switchColor updates colorIndex', () => {
    const wrapper = shallowMount(ColorSelector, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    vm.switchColor(2)
    expect(vm.state.colorIndex).toBe(2)
  })

  it('changeColorOption updates colors from colorCases', () => {
    const wrapper = shallowMount(ColorSelector, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    vm.state.colorForm.value = 'custom'
    vm.changeColorOption()
    expect(vm.state.colorForm.colors[0]).toBe('#ff0000')
  })
})
