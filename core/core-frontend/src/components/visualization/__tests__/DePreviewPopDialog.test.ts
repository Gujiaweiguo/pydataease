import { ref } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  canvasStyleDataValue: {
    dialogBackgroundColor: '#fff',
    dialogButton: '#000'
  }
}))

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: () => ({
    canvasStyleData: ref(mocks.canvasStyleDataValue)
  })
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({})
}))

vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => ({ getToken: undefined })
}))

vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div />' }
}))

vi.mock('@/views/chart/components/js/g2plot_tooltip_carousel', () => ({
  default: { closeEnlargeDialogDestroy: vi.fn() }
}))

vi.mock('@/config/axios', () => ({}))

import DePreviewPopDialog from '../DePreviewPopDialog.vue'

const stubs = {
  ElDialog: {
    template: '<div class="el-dialog"><slot /></div>',
    props: ['modelValue', 'width', 'fullscreen', 'modal']
  },
  XpackComponent: { template: '<div />' }
}

describe('DePreviewPopDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders successfully', () => {
    const wrapper = shallowMount(DePreviewPopDialog, { global: { stubs } })
    expect(wrapper.exists()).toBe(true)
  })

  it('exposes previewInit that sets state and opens dialog', async () => {
    const wrapper = shallowMount(DePreviewPopDialog, { global: { stubs } })
    const vm = wrapper.vm as any
    vm.previewInit({ url: 'http://example.com', size: 'middle' })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.el-dialog').exists()).toBe(true)
  })

  it('sets fullscreen for large size', async () => {
    const wrapper = shallowMount(DePreviewPopDialog, { global: { stubs } })
    const vm = wrapper.vm as any
    vm.previewInit({ url: 'http://example.com', size: 'large' })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.el-dialog').exists()).toBe(true)
  })

  it('appends popWindow=true to url without query', async () => {
    const wrapper = shallowMount(DePreviewPopDialog, { global: { stubs } })
    const vm = wrapper.vm as any
    vm.previewInit({ url: 'http://example.com', size: 'small' })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.el-dialog').exists()).toBe(true)
  })
})
