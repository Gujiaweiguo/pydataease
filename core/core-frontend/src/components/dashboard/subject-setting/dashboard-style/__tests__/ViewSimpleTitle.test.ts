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
    canvasStyleData: { component: { chartTitle: { color: '#000', fontSize: '14', isBolder: false, isItalic: false, hPosition: 'left' } } }
  })
}))

vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#5470c6']
}))

vi.mock('@/assets/svg/icon_bold_outlined.svg', () => ({ default: { template: '<svg />' } }))
vi.mock('@/assets/svg/icon_italic_outlined.svg', () => ({ default: { template: '<svg />' } }))
vi.mock('@/assets/svg/icon_left-alignment_outlined.svg', () => ({ default: { template: '<svg />' } }))
vi.mock('@/assets/svg/icon_center-alignment_outlined.svg', () => ({ default: { template: '<svg />' } }))
vi.mock('@/assets/svg/icon_right-alignment_outlined.svg', () => ({ default: { template: '<svg />' } }))

import ViewSimpleTitle from '@/components/dashboard/subject-setting/dashboard-style/ViewSimpleTitle.vue'

const stubs = {
  ElRow: { template: '<div><slot /></div>', props: ['class'] },
  ElSpace: { template: '<div><slot /></div>', props: ['wrap'] },
  ElFormItem: { template: '<div><slot /></div>', props: ['class'] },
  ElColorPicker: { template: '<div />', props: ['modelValue', 'isCustom', 'size', 'predefine'] },
  ElSelect: { template: '<select><slot /></select>', props: ['modelValue', 'size', 'placeholder', 'style'] },
  ElOption: { template: '<option><slot /></option>', props: ['label', 'value'] },
  ElTooltip: { template: '<div><slot /></div>', props: ['effect', 'placement'] },
  ElIcon: { template: '<i><slot /></i>' },
  Icon: { template: '<span><slot /></span>', props: ['name'] }
}

describe('ViewSimpleTitle', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders successfully', () => {
    const wrapper = shallowMount(ViewSimpleTitle, { global: { stubs } })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders custom-row container', () => {
    const wrapper = shallowMount(ViewSimpleTitle, { global: { stubs } })
    expect(wrapper.find('div').exists()).toBe(true)
  })
})
