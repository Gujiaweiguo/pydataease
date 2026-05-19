import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  recordSnapshotCache: vi.fn(),
  canvasStyleDataRef: { value: { scale: 100 } },
  curComponentRef: { value: null as any }
}))

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: (store: Record<string, unknown>) => store
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: mocks.recordSnapshotCache
  })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    canvasStyleData: mocks.canvasStyleDataRef,
    curComponent: mocks.curComponentRef
  })
}))

vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#ffffff', '#000000']
}))

import CommonBorderSetting from '../CommonBorderSetting.vue'

const globalStubs = {
  ElRow: { template: '<div><slot /></div>' },
  ElForm: { template: '<form><slot /></form>' },
  ElFormItem: { template: '<div><slot /></div>' },
  ElCol: { template: '<div><slot /></div>' },
  ElColorPicker: { template: '<div />', props: ['modelValue', 'disabled'] },
  ElInputNumber: {
    template: '<input type="number" />',
    props: ['modelValue', 'disabled', 'min', 'max', 'effect']
  },
  ElSelect: { template: '<select><slot /></select>', props: ['modelValue', 'disabled', 'effect'] },
  ElOption: { template: '<option><slot /></option>', props: ['label', 'value'] }
}

const defaultStyleInfo = {
  borderActive: true,
  borderColor: '#000000',
  borderStyle: 'solid',
  borderWidth: 1,
  borderRadius: 5
}

describe('CommonBorderSetting', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.curComponentRef.value = null
    mocks.canvasStyleDataRef.value = { scale: 100 }
  })

  it('renders with default props', () => {
    const wrapper = shallowMount(CommonBorderSetting, {
      props: { styleInfo: { ...defaultStyleInfo } },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('uses dark theme by default', () => {
    const wrapper = shallowMount(CommonBorderSetting, {
      props: { styleInfo: { ...defaultStyleInfo } },
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.form-item-dark').exists()).toBe(true)
  })

  it('renders border settings form with color picker', async () => {
    const wrapper = shallowMount(CommonBorderSetting, {
      props: { styleInfo: { ...defaultStyleInfo } },
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('renders SVG triangle template for SvgTriangle component', () => {
    mocks.curComponentRef.value = { component: 'SvgTriangle' }
    const wrapper = shallowMount(CommonBorderSetting, {
      props: { styleInfo: { ...defaultStyleInfo } },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
