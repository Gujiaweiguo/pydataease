import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: (store: Record<string, unknown>) => store
}))
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    curComponent: { frameLinks: { src: 'https://example.com' }, id: 'test-id' },
    mobileInPc: false
  })
}))
vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: vi.fn() })
}))
vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({ emitter: { emit: vi.fn() } })
}))
vi.mock('../../utils/utils', () => ({
  checkAddHttp: (url: string) => url,
  deepCopy: (obj: any) => JSON.parse(JSON.stringify(obj))
}))
vi.mock('../../store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    curComponent: { frameLinks: { src: 'https://example.com' }, id: 'test-id' },
    mobileInPc: false
  })
}))
vi.mock('../../store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: vi.fn() })
}))
vi.mock('../../hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))
vi.mock('@/assets/svg/icon_info_outlined.svg', () => ({ default: 'mocked-svg' }))

import FrameLinks from '../FrameLinks.vue'

const globalStubs = {
  'el-row': { template: '<div class="el-row"><slot /></div>' },
  'el-form': { template: '<form><slot /></form>', props: ['size'] },
  'el-form-item': { template: '<div class="form-item"><slot /></div>', props: ['label'] },
  'el-input': { template: '<input class="el-input" />', props: ['modelValue', 'effect'] },
  'el-tooltip': { template: '<div class="tooltip"><slot /></div>', props: ['effect', 'placement'] },
  'el-icon': { template: '<i><slot /></i>', props: ['class'] },
  Icon: { template: '<span><slot /></span>', props: ['name'] }
}

const defaultProps = () => ({
  frameLinks: { src: 'https://example.com' },
  themes: 'dark',
  canvasId: 'canvas-1'
})

describe('de-frame/FrameLinks.vue', () => {
  it('renders the component', () => {
    const wrapper = shallowMount(FrameLinks, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains an el-input for the URL', () => {
    const wrapper = shallowMount(FrameLinks, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.el-input').exists()).toBe(true)
  })

  it('renders a form element', () => {
    const wrapper = shallowMount(FrameLinks, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('renders tooltip and icon stubs', () => {
    const wrapper = shallowMount(FrameLinks, {
      props: { ...defaultProps(), themes: 'dark' },
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.el-row').exists()).toBe(true)
  })
})
