import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({ batchOptStatus: false, canvasStyleData: {} })
}))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#000', '#fff'],
  DEFAULT_LEGEND_STYLE: {
    show: true,
    color: '#333',
    fontSize: 12,
    hPosition: 'center',
    vPosition: 'top',
    orient: 'horizontal',
    icon: 'circle',
    size: 10,
    sort: 'none',
    customSort: []
  },
  DEFAULT_MISC: {}
}))
vi.mock('@/views/chart/components/js/util', () => ({ getDynamicColorScale: () => [] }))
vi.mock('@/hooks/web/useEmitt', () => ({ useEmitt: () => undefined }))
vi.mock('@/views/chart/components/editor/drag-item/components/CustomSortEdit.vue', () => ({
  default: { template: '<div />' }
}))
vi.mock('lodash-es', () => ({
  cloneDeep: (v: any) => JSON.parse(JSON.stringify(v)),
  get: (o: any, p: string) => {
    const keys = p.split('.')
    let r = o
    for (const k of keys) r = r?.[k]
    return r
  },
  set: (o: any, p: string, v: any) => {
    const keys = p.split('.')
    let r = o
    for (let i = 0; i < keys.length - 1; i++) r = r?.[keys[i]]
    r[keys[keys.length - 1]] = v
  }
}))
vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}), storeToRefs: (s: any) => ({ batchOptStatus: { value: false } }) }))
vi.mock('@/assets/svg/icon_left-align_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_horizontal-align_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_right-align_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_top-align_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_vertical-align_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_bottom-align_outlined.svg', () => ({ default: 'icon' }))

import LegendSelector from '../components/LegendSelector.vue'

const globalStubs = {
  ElForm: { template: '<form><slot /></form>', props: ['model', 'disabled', 'size'] },
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'class'] },
  ElRow: { template: '<div><slot /></div>', props: ['gutter'] },
  ElCol: { template: '<div><slot /></div>', props: ['span'] },
  ElSelect: {
    template: '<select><slot /></select>',
    props: ['modelValue', 'effect', 'size', 'disabled']
  },
  ElOption: { template: '<option><slot /></option>', props: ['key', 'label', 'value'] },
  ElColorPicker: { template: '<div />', props: ['modelValue', 'effect'] },
  ElCheckbox: {
    template: '<input type="checkbox" />',
    props: ['modelValue', 'effect', 'size', 'label']
  },
  ElRadioGroup: { template: '<div><slot /></div>', props: ['modelValue', 'size'] },
  ElRadio: {
    template: '<label><slot /></label>',
    props: ['effect', 'value', 'size', 'disabled', 'label']
  },
  ElSpace: { template: '<div><slot /></div>' },
  ElTooltip: { template: '<div><slot /></div>' },
  ElIcon: { template: '<i><slot /></i>' },
  ElInputNumber: {
    template: '<input type="number" />',
    props: ['modelValue', 'effect', 'precision', 'min', 'max', 'step', 'controls', 'disabled']
  },
  ElDialog: {
    template: '<div><slot /><slot name="footer" /></div>',
    props: ['title', 'visible', 'modelValue', 'width']
  },
  ElButton: { template: '<button><slot /></button>', props: ['type'] },
  Icon: { template: '<span><slot /></span>', props: ['name'] }
}

const defaultChart = () => ({
  type: 'bar',
  customStyle: {
    legend: {
      show: true,
      color: '#333',
      fontSize: 12,
      hPosition: 'center',
      vPosition: 'top',
      orient: 'horizontal',
      icon: 'circle',
      size: 10,
      sort: 'none',
      customSort: []
    }
  },
  customAttr: { misc: {} },
  xAxisExt: [],
  extStack: []
})

describe('LegendSelector', () => {
  it('renders with required props', () => {
    const wrapper = shallowMount(LegendSelector, {
      props: {
        chart: defaultChart(),
        themes: 'dark',
        propertyInner: ['icon', 'color', 'fontSize']
      },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('initializes legendForm from chart customStyle', () => {
    const wrapper = shallowMount(LegendSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: ['icon'] },
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.state.legendForm.show).toBe(true)
  })

  it('showProperty returns true for included props', () => {
    const wrapper = shallowMount(LegendSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: ['icon', 'color'] },
      global: { stubs: globalStubs }
    })
    expect((wrapper.vm as any).showProperty('icon')).toBe(true)
    expect((wrapper.vm as any).showProperty('orient')).toBe(false)
  })

  it('emits onLegendChange when changeLegendStyle is called', () => {
    const wrapper = shallowMount(LegendSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: ['icon'] },
      global: { stubs: globalStubs }
    })
    ;(wrapper.vm as any).changeLegendStyle('color')
    expect(wrapper.emitted('onLegendChange')).toBeTruthy()
  })

  it('computes chartType from chart prop', () => {
    const wrapper = shallowMount(LegendSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: [] },
      global: { stubs: globalStubs }
    })
    expect((wrapper.vm as any).chartType).toBe('bar')
  })

  it('computes toolTip as inverted theme', () => {
    const wrapper = shallowMount(LegendSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: [] },
      global: { stubs: globalStubs }
    })
    expect((wrapper.vm as any).toolTip).toBe('light')
  })
})
