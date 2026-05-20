import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import { ref } from 'vue'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    canvasStyleData: { scale: 100 },
    curComponent: { id: 'test', style: {} },
    canvasViewInfo: {}
  })
}))
vi.mock('pinia', async importOriginal => {
  const actual = (await importOriginal()) as any
  return {
    ...actual,
    storeToRefs: () => ({
      canvasStyleData: ref({ scale: 100 }),
      curComponent: ref({ id: 'test', style: {} })
    })
  }
})
vi.mock('@/custom-component/common/CanvasGroup.vue', () => ({
  default: { template: '<div class="canvas-group-stub"><slot /></div>' }
}))
vi.mock('@/utils/utils', () => ({ deepCopy: (v: any) => JSON.parse(JSON.stringify(v)) }))
vi.mock('@/views/chart/components/editor/util/dataVisualization', () => ({
  DEFAULT_CANVAS_STYLE_DATA_DARK: { scale: 100, width: 800, height: 600 }
}))
vi.mock('@/utils/style', () => ({ groupSizeStyleAdaptor: vi.fn() }))

import Component from '../Component.vue'

describe('group Component', () => {
  const defaultProps = {
    propValue: [],
    element: {
      id: 'group-1',
      style: { width: 400, height: 300 },
      propValue: null
    },
    showPosition: 'canvas',
    dvInfo: { id: 'dv-1' },
    searchCount: 0,
    isEdit: false,
    scale: 1,
    active: false,
    canvasViewInfo: {},
    fontFamily: 'inherit'
  }

  it('renders successfully with group class', () => {
    const wrapper = shallowMount(Component, { props: defaultProps })
    expect(wrapper.find('.group').exists()).toBe(true)
  })

  it('passes props correctly', () => {
    const wrapper = shallowMount(Component, { props: defaultProps })
    expect(wrapper.props('element')).toEqual(defaultProps.element)
    expect(wrapper.props('scale')).toBe(1)
    expect(wrapper.props('active')).toBe(false)
  })
})
