import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    batchOptStatus: false,
    mobileInPc: false,
    canvasStyleData: { component: { formatterItem: {} } },
    getViewPageInfo: () => null
  })
}))
vi.mock('@/store/modules/locale', () => ({
  useLocaleStoreWithOut: () => ({ getCurrentLocale: () => ({ lang: 'zh' }) })
}))
vi.mock('@/store/modules/map', () => ({
  useMapStoreWithOut: () => ({
    mapKey: { key: '', securityCode: '', mapType: 'gaode' },
    setKey: () => undefined
  })
}))
vi.mock('@/api/setting/sysParameter', () => ({
  queryMapKeyApi: () => Promise.resolve({ data: { key: '', securityCode: '', mapType: 'gaode' } })
}))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#000', '#fff'],
  DEFAULT_BASIC_STYLE: {
    colors: ['#3370ff', '#04b49c'],
    alpha: 100,
    gradient: false,
    lineWidth: 2,
    lineSymbol: 'circle',
    lineSymbolSize: 4,
    lineSmooth: false,
    radarShape: 'polygon',
    gaugeStyle: 'default',
    mapStyle: 'normal',
    mapSymbol: 'circle',
    mapSymbolSize: 10,
    mapSymbolOpacity: 80,
    mapSymbolStrokeWidth: 0,
    tableLayoutMode: 'grid',
    tableColumnMode: 'adapt',
    tableColumnWidth: 100,
    tableFieldWidth: [],
    tablePageMode: 'page',
    tablePageStyle: 'simple',
    tablePageSize: 20,
    barDefault: true,
    barGap: 0,
    columnWidthRatio: 60,
    scatterSymbol: 'circle',
    scatterSymbolSize: 10,
    tableBorderColor: '#ccc',
    tableScrollBarColor: '#999',
    radiusColumnBar: 'rightAngle',
    layout: 'vertical',
    customIcon: '',
    mapStyleUrl: '',
    quotaPosition: 'col',
    quotaColLabel: '',
    innerRadius: 0,
    radius: 80,
    heatMapType: 'heatmap',
    heatMapIntensity: 1,
    heatMapRadius: 10,
    defaultExpandLevel: 'all',
    tableRowHeaderMode: 'adapt',
    tableRowHeaderWidth: 120,
    tableRowHeaderWidthPercent: 30,
    autoWrap: false,
    maxLines: 1,
    showHoverStyle: true,
    showLabel: true,
    autoFit: true,
    zoomLevel: 5,
    mapCenter: { longitude: 116, latitude: 39 },
    showZoom: false,
    zoomButtonColor: '#333',
    zoomBackground: '#fff',
    gaugeAxisLine: true,
    gaugePercentLabel: true,
    radarShowPoint: true,
    radarPointSize: 4,
    radarAreaColor: false,
    calcTopN: false,
    topN: 5,
    topNLabel: '',
    topRoundAngle: false,
    roundAngle: false,
    radiusColumn: 'rightAngle',
    columnWidthRatioValue: 60,
    showRange: false,
    symbol: 'circle',
    symbolSize: 10,
    symbolOpacity: 80,
    symbolStrokeWidth: 0,
    customColor: null,
    colorIndex: 0,
    mergeCells: false,
    tableRowHeaderWidthValue: 120
  },
  DEFAULT_MISC: { mapPitch: 0 }
}))
vi.mock(
  '@/views/chart/components/editor/editor-style/components/CustomColorStyleSelect.vue',
  () => ({
    default: { template: '<div />' }
  })
)
vi.mock('@/views/chart/components/js/util', () => ({ svgStrToUrl: () => '' }))
vi.mock('@/views/chart/components/js/panel/common/common_antv', () => ({
  numberToChineseUnderHundred: (n: number) => String(n)
}))
vi.mock('@/views/chart/components/js/panel/charts/map/common', () => ({
  gaodeMapStyleOptions: [],
  qqMapStyleOptions: [],
  tdtMapStyleOptions: []
}))
vi.mock('@/hooks/web/useEmitt', () => ({ useEmitt: () => undefined }))
vi.mock('lodash-es', () => ({
  cloneDeep: (v: any) => JSON.parse(JSON.stringify(v)),
  defaultsDeep: (t: any, ...s: any[]) => Object.assign({}, ...s, t),
  debounce: (fn: any) => fn,
  isNumber: (v: any) => typeof v === 'number',
  find: (arr: any[], fn: any) => arr.find(fn)
}))
vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: () => ({ batchOptStatus: { value: false }, mobileInPc: { value: false } })
}))
vi.mock('element-plus-secondary', () => ({
  ElFormItem: { template: '<div><slot /></div>' },
  ElInputNumber: { template: '<input type="number" />' },
  ElMessage: { warning: () => undefined }
}))
vi.mock('@/assets/svg/icon_info_outlined.svg', () => ({ default: 'icon' }))

import BasicStyleSelector from '../components/BasicStyleSelector.vue'

const globalStubs = {
  ElForm: { template: '<form><slot /></form>', props: ['size'] },
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'class'] },
  ElRow: { template: '<div><slot /></div>', props: ['gutter'] },
  ElCol: { template: '<div><slot /></div>', props: ['span'] },
  ElSelect: {
    template: '<select><slot /></select>',
    props: ['modelValue', 'effect', 'size', 'disabled', 'filterable', 'multiple']
  },
  ElOption: { template: '<option><slot /></option>', props: ['key', 'label', 'value'] },
  ElColorPicker: { template: '<div />', props: ['modelValue', 'effect'] },
  ElCheckbox: {
    template: '<input type="checkbox" />',
    props: ['modelValue', 'effect', 'size', 'label', 'disabled']
  },
  ElRadioGroup: { template: '<div><slot /></div>', props: ['modelValue', 'size', 'effect'] },
  ElRadio: { template: '<label><slot /></label>', props: ['effect', 'value', 'label'] },
  ElInput: {
    template: '<input />',
    props: ['modelValue', 'effect', 'type', 'min', 'max', 'size', 'disabled', 'controls']
  },
  ElInputNumber: {
    template: '<input type="number" />',
    props: [
      'modelValue',
      'effect',
      'min',
      'max',
      'step',
      'size',
      'disabled',
      'precision',
      'showInputControls',
      'controlsPosition'
    ]
  },
  ElSlider: { template: '<div />', props: ['modelValue', 'effect', 'min', 'max', 'step'] },
  ElTooltip: { template: '<div><slot /></div>' },
  ElIcon: { template: '<i><slot /></i>' },
  Icon: { template: '<span><slot /></span>', props: ['name'] }
}

const defaultChart = () => ({
  type: 'bar',
  xAxis: [],
  yAxis: [],
  customAttr: {
    basicStyle: {
      colors: ['#3370ff', '#04b49c'],
      alpha: 100,
      gradient: false,
      layout: 'vertical',
      tableLayoutMode: 'grid',
      tableColumnMode: 'adapt',
      tableColumnWidth: 100,
      tableFieldWidth: [],
      tablePageMode: 'page',
      tablePageStyle: 'simple',
      tablePageSize: 20,
      barDefault: true,
      barGap: 0,
      columnWidthRatio: 60,
      radiusColumnBar: 'rightAngle',
      gaugeAxisLine: true,
      gaugePercentLabel: true
    },
    misc: { mapPitch: 0 },
    tableHeader: { showIndex: false, indexLabel: '' },
    tableCell: { mergeCells: false }
  }
})

describe('BasicStyleSelector', () => {
  it('renders with required props', async () => {
    const wrapper = shallowMount(BasicStyleSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: ['alpha', 'gradient'] },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('showProperty returns correct value', async () => {
    const wrapper = shallowMount(BasicStyleSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: ['alpha', 'gradient'] },
      global: { stubs: globalStubs }
    })
    expect((wrapper.vm as any).showProperty('alpha')).toBe(true)
    expect((wrapper.vm as any).showProperty('lineWidth')).toBe(false)
  })

  it('emits onBasicStyleChange when changeBasicStyle is called', async () => {
    const wrapper = shallowMount(BasicStyleSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: ['alpha'] },
      global: { stubs: globalStubs }
    })
    ;(wrapper.vm as any).changeBasicStyle('alpha')
    expect(wrapper.emitted('onBasicStyleChange')).toBeTruthy()
  })

  it('onAlphaChange clamps value within 0-100', async () => {
    const wrapper = shallowMount(BasicStyleSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: ['alpha'] },
      global: { stubs: globalStubs }
    })
    ;(wrapper.vm as any).onAlphaChange('150')
    expect((wrapper.vm as any).state.basicStyleForm.alpha).toBe(100)
  })

  it('emits onMiscChange when changeMisc is called', async () => {
    const wrapper = shallowMount(BasicStyleSelector, {
      props: { chart: defaultChart(), themes: 'dark', propertyInner: ['alpha'] },
      global: { stubs: globalStubs }
    })
    ;(wrapper.vm as any).changeMisc('mapPitch')
    expect(wrapper.emitted('onMiscChange')).toBeTruthy()
  })
})
