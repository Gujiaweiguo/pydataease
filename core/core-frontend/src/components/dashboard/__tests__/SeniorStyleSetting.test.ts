import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  recordSnapshotCache: vi.fn()
}))

vi.mock('pinia', async () => {
  const actual = await vi.importActual('pinia')
  return { ...actual }
})

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    canvasStyleData: {
      component: {
        seniorStyleSetting: {
          linkageIconColor: '#000',
          drillLayerColor: '#000'
        }
      }
    }
  })
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: mocks.recordSnapshotCache })
}))

vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#000000', '#ffffff']
}))

vi.mock('@/utils/eventBus', () => ({
  default: { on: vi.fn(), off: vi.fn(), emit: vi.fn() }
}))

vi.mock('@/config/axios', () => ({}))

import SeniorStyleSetting from '@/components/dashboard/subject-setting/dashboard-style/SeniorStyleSetting.vue'

const stubs = {
  ElForm: { template: '<form><slot /></form>', props: ['labelPosition'] },
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'effect', 'class'] },
  ElRow: { template: '<div><slot /></div>', props: ['gutter'] },
  ElCol: { template: '<div><slot /></div>', props: ['span'] },
  ElColorPicker: { template: '<input type="color" />', props: ['modelValue', 'effect', 'size', 'triggerWidth', 'isCustom', 'predefine'] }
}

describe('SeniorStyleSetting', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders successfully', () => {
    const wrapper = shallowMount(SeniorStyleSetting, { global: { stubs } })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders two color picker fields', () => {
    const wrapper = shallowMount(SeniorStyleSetting, { global: { stubs } })
    expect(wrapper.findAll('input[type="color"]').length).toBe(2)
  })

  it('accepts themes prop', () => {
    const wrapper = shallowMount(SeniorStyleSetting, {
      props: { themes: 'dark' },
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
