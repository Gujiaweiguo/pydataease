import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  DEFAULT_MISC: {
    gaugeStartAngle: 225,
    gaugeEndAngle: -45,
    gaugeMinType: 'fix',
    gaugeMin: 0,
    gaugeMinField: { id: '', summary: '' },
    gaugeMaxType: 'fix',
    gaugeMax: undefined,
    gaugeMaxField: { id: '', summary: '' },
    liquidMaxType: 'fix',
    liquidMax: undefined,
    liquidMaxField: { id: '', summary: '' },
    liquidShowBorder: true,
    liquidBorderWidth: 2,
    liquidBorderDistance: 3,
    liquidShape: 'circle',
    liquidSize: 80,
    wordCloudAxisValueRange: { auto: true, min: 0, max: 0, fieldId: '' },
    wordSizeRange: [8, 32],
    wordSpacing: 5
  }
}))
vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => undefined
}))
vi.mock('lodash-es', () => ({
  cloneDeep: (v: any) => JSON.parse(JSON.stringify(v)),
  defaultsDeep: (t: any, ...s: any[]) => Object.assign({}, ...s, t)
}))
vi.mock('@/utils/attr', () => ({
  fieldType: { 0: 'text', 1: 'time', 2: 'value', 3: 'value' }
}))
vi.mock('@/components/icon-group/field-list', () => ({
  iconFieldMap: { text: 'div', time: 'div', value: 'div' }
}))
vi.mock('@/assets/svg/icon_info_outlined.svg', () => ({ default: 'icon' }))

import MiscSelector from '../MiscSelector.vue'

const globalStubs = {
  ElForm: { template: '<form><slot /></form>', props: ['size', 'model'] },
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'class', 'vShow'] },
  ElRow: { template: '<div><slot /></div>', props: ['gutter'] },
  ElCol: { template: '<div><slot /></div>', props: ['span'] },
  ElInputNumber: {
    template: '<input type="number" />',
    props: ['modelValue', 'effect', 'min', 'max', 'size', 'controlsPosition', 'disabled']
  },
  ElSelect: {
    template: '<select><slot /></select>',
    props: ['modelValue', 'effect', 'placeholder', 'class', 'disabled']
  },
  ElOption: { template: '<option><slot /></option>', props: ['key', 'label', 'value'] },
  ElRadioGroup: {
    template: '<div><slot /></div>',
    props: ['modelValue', 'effect', 'size', 'disabled']
  },
  ElRadio: { template: '<label><slot /></label>', props: ['effect', 'label'] },
  ElCheckbox: {
    template: '<input type="checkbox" />',
    props: ['modelValue', 'effect', 'size', 'label']
  },
  ElSlider: { template: '<div />', props: ['modelValue', 'effect', 'min', 'max', 'range'] },
  ElTooltip: { template: '<div><slot /></div>', props: ['effect', 'placement'] },
  ElIcon: { template: '<i><slot /></i>' },
  Icon: { template: '<span><slot /></span>', props: ['name', 'className'] }
}

const defaultProps = () => ({
  chart: {
    type: 'gauge',
    customAttr: {
      misc: {
        gaugeStartAngle: 225,
        gaugeEndAngle: -45,
        gaugeMinType: 'fix',
        gaugeMin: 0,
        gaugeMinField: { id: '', summary: '' },
        gaugeMaxType: 'fix',
        gaugeMax: 100,
        gaugeMaxField: { id: '', summary: '' },
        liquidMaxType: 'fix',
        liquidMax: 100,
        liquidMaxField: { id: '', summary: '' },
        liquidShowBorder: true,
        liquidBorderWidth: 2,
        liquidBorderDistance: 3,
        liquidShape: 'circle',
        liquidSize: 80,
        wordCloudAxisValueRange: { auto: true, min: 0, max: 0, fieldId: '' },
        wordSizeRange: [8, 32],
        wordSpacing: 5
      }
    },
    yAxis: [{ id: 'y1' }]
  },
  themes: 'dark',
  quotaFields: [{ id: 'q1', name: 'Quota', deType: 2, summary: 'sum' }]
})

const mountProps = () => defaultProps() as any

describe('MiscSelector', () => {
  it('renders with required props', () => {
    const wrapper = shallowMount(MiscSelector, {
      props: mountProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('initializes miscForm from chart customAttr', () => {
    const wrapper = shallowMount(MiscSelector, {
      props: mountProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.state.miscForm.gaugeStartAngle).toBe(225)
    expect(vm.state.miscForm.gaugeEndAngle).toBe(-45)
  })

  it('isLiquid computed returns true for liquid type', () => {
    const props = defaultProps()
    props.chart.type = 'liquid'
    const wrapper = shallowMount(MiscSelector, {
      props: props as any,
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.isLiquid).toBe(true)
    expect(vm.isGauge).toBe(false)
  })

  it('emits onMiscChange when changeMisc is called', () => {
    const wrapper = shallowMount(MiscSelector, {
      props: mountProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    vm.changeMisc('gaugeStartAngle')
    expect(wrapper.emitted('onMiscChange')).toBeTruthy()
  })

  it('showProperty returns true for included properties', () => {
    const props = defaultProps()
    ;(props as any).propertyInner = ['gaugeStartAngle', 'gaugeEndAngle']
    const wrapper = shallowMount(MiscSelector, {
      props: props as any,
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.showProperty('gaugeStartAngle')).toBe(true)
    expect(vm.showProperty('wordSpacing')).toBe(false)
  })
})
