import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/api/visualization/visualizationBackground', () => ({
  queryVisualizationBackground: vi.fn(() => Promise.resolve({ data: { default: [] } }))
}))

vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#ffffff', '#000000']
}))

vi.mock('@/utils/imgUtils', () => ({
  imgUrlTrans: (url: string) => url
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCacheToMobile: vi.fn()
  })
}))

vi.mock('@/api/staticResource', () => ({
  beforeUploadCheck: vi.fn(),
  uploadFileResult: vi.fn()
}))

vi.mock('@/utils/utils', () => ({
  deepCopy: (obj: any) => JSON.parse(JSON.stringify(obj))
}))

vi.mock('@/Types', () => ({
  ShorthandMode: { Uniform: 'uniform', Axis: 'axis', PerEdge: 'perEdge' }
}))

vi.mock('element-resize-detector', () => ({
  default: () => ({
    listenTo: vi.fn(),
    removeAllListeners: vi.fn(),
    uninstall: vi.fn()
  })
}))

import BackgroundOverallCommon from '../BackgroundOverallCommon.vue'

const mountComponent = () =>
  shallowMount(BackgroundOverallCommon, {
    props: {
      commonBackgroundPop: {
        innerPadding: { mode: 'uniform', top: 8, right: 8, bottom: 8, left: 8 },
        borderRadius: { mode: 'uniform', topLeft: 4, topRight: 4, bottomLeft: 4, bottomRight: 4 },
        backgroundColorSelect: false,
        backgroundColor: '#ffffff',
        backgroundImageEnable: false,
        backgroundType: 'innerImage',
        innerImageColor: '#000000',
        innerImage: 'board/board_1.svg',
        outerImage: null
      },
      themes: 'dark'
    },
    global: {
      mocks: {
        $t: (key: string) => key
      },
      stubs: {
        'el-form': { template: '<div><slot /></div>' },
        'el-form-item': { template: '<div><slot /></div>' },
        'el-row': { template: '<div><slot /></div>' },
        'el-col': { template: '<div><slot /></div>' },
        'el-checkbox': { template: '<div><slot /></div>' },
        'el-color-picker': { template: '<div />' },
        'el-radio-group': { template: '<div><slot /></div>' },
        'el-radio': { template: '<div><slot /></div>' },
        'el-select': { template: '<div><slot /></div>' },
        'el-option': { template: '<div />' },
        'el-upload': { template: '<div><slot /></div>' },
        'el-icon': { template: '<i><slot /></i>' },
        'el-button': { template: '<button><slot /></button>' },
        'el-input-number': { template: '<div />' },
        'board-item': true,
        'border-option-prefix': true,
        'img-view-dialog': true
      }
    }
  })

describe('BackgroundOverallCommon', () => {
  it('renders the root container', () => {
    const wrapper = mountComponent()

    expect(wrapper.find('div[style*="width: 100%"]').exists()).toBe(true)
  })

  it('accepts commonBackgroundPop prop', () => {
    const wrapper = mountComponent()
    const props = wrapper.props() as any

    expect(props.commonBackgroundPop).toBeDefined()
    expect(props.commonBackgroundPop.innerPadding.top).toBe(8)
  })

  it('emits onBackgroundChange event', async () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.onBackgroundChange()
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('onBackgroundChange')).toBeTruthy()
  })
})
