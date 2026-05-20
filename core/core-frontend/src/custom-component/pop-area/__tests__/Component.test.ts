import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('pinia', async (importOriginal) => {
  const actual: any = await importOriginal()
  return {
    ...actual,
    storeToRefs: (store: any) => {
      const refs: Record<string, { value: any }> = {}
      for (const key of Object.keys(store)) {
        refs[key] = { value: store[key] }
      }
      return refs
    }
  }
})
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    curComponent: null,
    canvasStyleData: {},
    addComponent: vi.fn()
  })
}))
vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: vi.fn()
  })
}))
vi.mock('@/utils/canvasUtils', () => ({ findDragComponent: vi.fn() }))
vi.mock('@/views/visualized/data/dataset/form/util', () => ({ guid: () => 'test-guid' }))
vi.mock('@/utils/changeComponentsSizeWithScale', () => ({
  changeComponentSizeWithScale: vi.fn()
}))
vi.mock('@/utils/canvasStyle', () => ({ adaptCurThemeCommonStyle: vi.fn() }))
vi.mock('@/utils/eventBus', () => ({
  default: { on: vi.fn(), off: vi.fn() }
}))
vi.mock('@/components/data-visualization/canvas/ComponentWrapper.vue', () => ({
  default: { template: '<div class="component-wrapper-stub"></div>' }
}))
vi.mock('element-plus-secondary', () => ({
  ElMessage: { error: vi.fn() }
}))

import Component from '../Component.vue'

describe('pop-area/Component.vue', () => {
  const createProps = (overrides = {}) => ({
    dvInfo: { id: 'test-dv' },
    canvasStyleData: { height: 800 },
    popComponentData: [],
    canvasViewInfo: {},
    canvasId: 'canvas-main',
    scale: 1,
    showPosition: 'preview',
    canvasState: { curPointArea: 'hidden' },
    ...overrides
  })

  it('renders the component', () => {
    const wrapper = shallowMount(Component, {
      props: createProps(),
      global: {
        stubs: { ComponentWrapper: true }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the pop-area container', () => {
    const wrapper = shallowMount(Component, {
      props: createProps(),
      global: {
        stubs: { ComponentWrapper: true }
      }
    })
    expect(wrapper.find('.pop-area').exists()).toBe(true)
  })

  it('shows preview-pop class when showPosition is preview', () => {
    const wrapper = shallowMount(Component, {
      props: createProps({ showPosition: 'preview' }),
      global: {
        stubs: { ComponentWrapper: true }
      }
    })
    expect(wrapper.find('.preview-pop').exists()).toBe(true)
  })

  it('renders pop-area-main when no popComponentData and showPosition is popEdit', () => {
    const wrapper = shallowMount(Component, {
      props: createProps({ popComponentData: [], showPosition: 'popEdit' }),
      global: {
        stubs: { ComponentWrapper: true }
      }
    })
    expect(wrapper.find('.pop-area-main').exists()).toBe(true)
  })
})
