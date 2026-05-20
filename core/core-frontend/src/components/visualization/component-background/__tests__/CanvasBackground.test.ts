import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: (store: Record<string, unknown>) => store
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#ffffff', '#000000']
}))

vi.mock('@/utils/imgUtils', () => ({
  imgUrlTrans: (url: string) => url
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: vi.fn()
  })
}))

vi.mock('@/api/staticResource', () => ({
  beforeUploadCheck: vi.fn(),
  uploadFileResult: vi.fn()
}))

vi.mock('@/store/modules/data-visualization/dvMain', async () => {
  const { ref } = await import('vue')
  const canvasStyleData = ref({
    backgroundColorSelect: false,
    backgroundColor: '#ffffff',
    backgroundImageEnable: false,
    background: null,
    dialogBackgroundColor: '#ffffff',
    dialogButton: '#3370ff'
  })
  const dvInfo = ref({
    selfWatermarkStatus: false,
    watermarkInfo: null
  })
  return {
    dvMainStoreWithOut: () => ({
      canvasStyleData,
      dvInfo
    })
  }
})

import CanvasBackground from '../CanvasBackground.vue'

const mountComponent = () =>
  shallowMount(CanvasBackground, {
    props: {
      themes: 'dark'
    },
    global: {
      stubs: {
        'el-form': { template: '<div><slot /></div>' },
        'el-form-item': { template: '<div><slot /></div>' },
        'el-row': { template: '<div><slot /></div>' },
        'el-checkbox': { template: '<div><slot /></div>' },
        'el-color-picker': { template: '<div />' },
        'el-upload': { template: '<div><slot /></div>' },
        'el-icon': { template: '<i><slot /></i>' },
        'el-button': { template: '<button><slot /></button>' },
        'el-divider': { template: '<hr />' },
        'img-view-dialog': true
      }
    }
  })

describe('CanvasBackground', () => {
  it('renders the root container', () => {
    const wrapper = mountComponent()

    expect(wrapper.find('div[style*="width: 100%"]').exists()).toBe(true)
  })

  it('accepts themes prop with default dark', () => {
    const wrapper = mountComponent()
    const props = wrapper.props() as any

    expect(props.themes).toBe('dark')
  })
})
