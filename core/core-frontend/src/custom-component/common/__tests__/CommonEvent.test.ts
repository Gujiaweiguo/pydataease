import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  recordSnapshotCacheToMobile: vi.fn(),
  dvInfoType: 'dashboard'
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
    recordSnapshotCacheToMobile: mocks.recordSnapshotCacheToMobile
  })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    dvInfo: { type: mocks.dvInfoType }
  })
}))

vi.mock('@/assets/svg/icon_info_outlined.svg', () => ({ default: 'mocked-svg' }))

import CommonEvent from '../CommonEvent.vue'

const globalStubs = {
  'el-row': { template: '<div><slot /></div>' },
  'el-form': { template: '<form><slot /></form>' },
  'el-form-item': { template: '<div><slot /></div>' },
  'el-checkbox': { template: '<input type="checkbox" />', props: ['modelValue'] },
  'el-tooltip': { template: '<div><slot /><slot name="content" /></div>' },
  'el-icon': { template: '<i><slot /></i>' },
  'el-select': { template: '<select><slot /></select>', props: ['modelValue', 'disabled'] },
  'el-option': { template: '<option><slot /></option>', props: ['label', 'value'] },
  'el-input': { template: '<input />', props: ['modelValue', 'disabled'] },
  'el-radio-group': { template: '<div><slot /></div>', props: ['modelValue', 'disabled'] },
  'el-radio': { template: '<label><slot /></label>', props: ['label'] },
  Icon: { template: '<span><slot /></span>' }
}

const defaultEventsInfo = {
  checked: false,
  type: 'jump',
  typeList: [
    { key: 'jump', label: 'jump' },
    { key: 'showHidden', label: 'showHidden' },
    { key: 'refreshDataV', label: 'refreshDataV' },
    { key: 'download', label: 'download' },
    { key: 'fullScreen', label: 'fullScreen' }
  ],
  jump: { value: '', type: '_blank' }
}

describe('CommonEvent', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.dvInfoType = 'dashboard'
  })

  it('renders with default props', () => {
    const wrapper = shallowMount(CommonEvent, {
      props: { eventsInfo: { ...defaultEventsInfo } },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('uses dark theme by default', () => {
    const wrapper = shallowMount(CommonEvent, {
      props: { eventsInfo: { ...defaultEventsInfo } },
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.form-item-dark').exists()).toBe(true)
  })

  it('uses light theme when themes prop is light', () => {
    const wrapper = shallowMount(CommonEvent, {
      props: { themes: 'light', eventsInfo: { ...defaultEventsInfo } },
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.form-item-light').exists()).toBe(true)
  })

  it('renders the enable event binding checkbox', () => {
    const wrapper = shallowMount(CommonEvent, {
      props: { eventsInfo: { ...defaultEventsInfo } },
      global: { stubs: globalStubs }
    })
    const checkbox = wrapper.find('input[type="checkbox"]')
    expect(checkbox.exists()).toBe(true)
  })
})
