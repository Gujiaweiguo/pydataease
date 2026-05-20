import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import { ref } from 'vue'

const mobileSetting = {
  backgroundColorSelect: false,
  background: '',
  color: '#ffffff',
  backgroundImageEnable: false,
  customSetting: false
}

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    canvasStyleData: { mobileSetting },
    setCanvasStyle: vi.fn()
  })
}))
vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: vi.fn() })
}))
vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: vi.fn(() => ({ emitter: { emit: vi.fn(), on: vi.fn() } }))
}))
vi.mock('@/utils/imgUtils', () => ({ imgUrlTrans: vi.fn(v => v) }))
vi.mock('@/utils/utils', () => ({ deepCopy: vi.fn(v => v), getLocale: vi.fn(() => 'zh') }))
vi.mock('@/api/staticResource', () => ({ beforeUploadCheck: vi.fn(), uploadFileResult: vi.fn() }))
vi.mock('pinia', () => ({
  createPinia: vi.fn(() => ({})),
  storeToRefs: (store: any) => ({ canvasStyleData: ref(store.canvasStyleData) }),
  defineStore: vi.fn()
}))
vi.mock('lodash-es', () => ({ cloneDeep: vi.fn(v => v) }))
vi.mock('@/views/chart/components/editor/util/chart', () => ({ COLOR_PANEL: [] }))

import MobileBackgroundSelector from '../MobileBackgroundSelector.vue'

describe('MobileBackgroundSelector', () => {
  it('renders component', () => {
    const wrapper = shallowMount(MobileBackgroundSelector, {
      props: { themes: 'light' },
      global: {
        stubs: {
          'el-checkbox': true,
          'el-form': { template: '<div><slot /></div>' },
          'el-form-item': { template: '<div><slot /></div>' },
          'el-color-picker': true,
          'el-upload': true,
          'el-icon': { template: '<div><slot /></div>' },
          'el-row': { template: '<div><slot /></div>' },
          'el-button': true,
          'img-view-dialog': true,
          Plus: true
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains mobile-background-selector wrapper', () => {
    const wrapper = shallowMount(MobileBackgroundSelector, {
      props: { themes: 'light' },
      global: {
        stubs: {
          'el-checkbox': true,
          'el-form': { template: '<div><slot /></div>' },
          'el-form-item': { template: '<div><slot /></div>' },
          'el-color-picker': true,
          'el-upload': true,
          'el-icon': { template: '<div><slot /></div>' },
          'el-row': { template: '<div><slot /></div>' },
          'el-button': true,
          'img-view-dialog': true,
          Plus: true
        }
      }
    })
    expect(wrapper.find('.mobile-background-selector').exists()).toBe(true)
  })
})
