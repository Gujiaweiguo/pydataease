import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/store', () => ({ store: {} }))

vi.mock('pinia', () => ({
  defineStore: vi.fn(),
  storeToRefs: vi.fn(() => ({})),
  createPinia: vi.fn()
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    canvasStyleData: { component: { seniorStyleSetting: { linkageIconColor: '#000', drillLayerColor: '#000' } } }
  })
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: vi.fn() })
}))

vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#5470c6']
}))

vi.mock('@/utils/eventBus', () => ({
  default: { on: vi.fn(), off: vi.fn(), emit: vi.fn() }
}))

vi.mock('lodash-es', () => ({
  cloneDeep: (v: any) => JSON.parse(JSON.stringify(v))
}))

import SeniorStyleSetting from '@/components/dashboard/subject-setting/dashboard-style/SeniorStyleSetting.vue'

const stubs = {
  ElForm: { template: '<form><slot /></form>', props: ['labelPosition'] },
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'class', 'effect'] },
  ElRow: { template: '<div><slot /></div>', props: ['gutter'] },
  ElCol: { template: '<div><slot /></div>', props: ['span'] },
  ElColorPicker: { template: '<div />', props: ['modelValue', 'effect', 'size', 'triggerWidth', 'isCustom', 'predefine'] }
}

describe('SeniorStyleSetting', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders successfully', () => {
    const wrapper = shallowMount(SeniorStyleSetting, { global: { stubs } })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts themes prop', () => {
    const wrapper = shallowMount(SeniorStyleSetting, {
      props: { themes: 'dark' },
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders form container', () => {
    const wrapper = shallowMount(SeniorStyleSetting, { global: { stubs } })
    expect(wrapper.find('div').exists()).toBe(true)
  })
})
