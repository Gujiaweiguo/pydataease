import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('@/config/axios/service', () => ({}))

vi.mock('@/config/axios/refresh', () => ({}))

vi.mock('@/config/axios/hmac', () => ({}))

vi.mock('@/store/modules/user', () => ({
  useUserStoreWithOut: vi.fn(() => ({}))
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: vi.fn()
  })
}))

vi.mock('@/utils/canvasUtils', () => ({
  initCanvasData: vi.fn(),
  initCanvasDataPrepare: vi.fn(),
  onInitReady: vi.fn(),
  getMapElementIds: vi.fn(() => [])
}))

vi.mock('@/utils/imgUtils', () => ({
  download2AppTemplate: vi.fn(),
  downloadCanvas2: vi.fn()
}))

vi.mock('@/components/data-visualization/canvas/DePreview.vue', () => ({
  default: {
    template: '<div class="de-preview-stub" />',
    methods: { restore: vi.fn(), getPreviewCanvasSize: vi.fn(() => ({ innerWidth: 1920, innerHeight: 1080 })) }
  }
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    fullscreenFlag: false
  })
}))

vi.mock('pinia', async importOriginal => {
  const actual = await importOriginal() as Record<string, unknown>
  return {
    ...actual,
    storeToRefs: vi.fn(() => ({
      fullscreenFlag: { value: false }
    }))
  }
})

import DvPreview from '../DvPreview.vue'

const globalStubs = {
  DePreview: { template: '<div class="de-preview-stub" />' }
}

describe('DvPreview', () => {
  const defaultProps = {
    canvasStylePreview: { screenAdaptor: 'widthFirst' },
    canvasDataPreview: [],
    canvasViewInfoPreview: {},
    dvInfo: { id: '1', name: 'Test', type: 'dataV' },
    curPreviewGap: 0,
    showPosition: 'preview',
    downloadStatus: false
  }

  const mountComponent = () =>
    shallowMount(DvPreview, {
      props: defaultProps,
      global: { stubs: globalStubs }
    })

  it('renders', () => {
    const wrapper = mountComponent()
    expect(wrapper.exists()).toBe(true)
  })

  it('has content-outer wrapper', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('.content-outer').exists()).toBe(true)
  })

  it('has content-inner wrapper', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('.content-inner').exists()).toBe(true)
  })

  it('exposes restore method', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any
    expect(typeof vm.restore).toBe('function')
  })
})
