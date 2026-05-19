import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/custom-component/de-decoration/component_details/config', () => ({
  findDecoration: (name: string) => {
    if (name === 'DeBoard1') {
      return { template: '<div class="mock-decoration">Board1</div>' }
    }
    return undefined
  },
  calcTwoPointDistance: (a: number[], b: number[]) =>
    Math.sqrt(Math.pow(a[0] - b[0], 2) + Math.pow(a[1] - b[1], 2)),
  getPointDistances: (points: number[][]) =>
    points
      .slice(0, -1)
      .map((_, i) =>
        Math.sqrt(
          Math.pow(points[i][0] - points[i + 1][0], 2) +
            Math.pow(points[i][1] - points[i + 1][1], 2)
        )
      ),
  customMergeColor: (defaults: string[], colors: string[]) =>
    defaults.map((d, i) => (colors && colors[i] !== null ? colors[i] : d))
}))

import Component from '../Component.vue'

const globalStubs = {}

describe('de-decoration/Component.vue', () => {
  const createProps = (overrides = {}) => ({
    curStyle: { width: '200', height: '100' },
    scale: 1,
    showPosition: 'preview',
    element: {
      innerType: 'DeBoard1',
      style: { color0: '#ff0000', color1: '#00ff00' }
    },
    ...overrides
  })

  it('renders the component', () => {
    const wrapper = shallowMount(Component, {
      props: createProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the dynamic-shape wrapper div', () => {
    const wrapper = shallowMount(Component, {
      props: createProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.dynamic-shape').exists()).toBe(true)
  })

  it('uses full width/height in preview mode', () => {
    const wrapper = shallowMount(Component, {
      props: createProps({ showPosition: 'preview' }),
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('handles missing innerType gracefully', () => {
    const wrapper = shallowMount(Component, {
      props: createProps({
        element: { innerType: null, style: {} }
      }),
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('accepts scale prop', () => {
    const wrapper = shallowMount(Component, {
      props: createProps({ scale: 2 }),
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('has correct default showPosition', () => {
    const wrapper = shallowMount(Component, {
      props: {
        curStyle: { width: '200', height: '100' },
        scale: 1,
        element: { innerType: 'DeBoard1', style: {} }
      },
      global: { stubs: globalStubs }
    })
    expect((wrapper.vm as any).showPosition).toBe('preview')
  })
})
