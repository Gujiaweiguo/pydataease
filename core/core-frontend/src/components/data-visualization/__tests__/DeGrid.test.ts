import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/config/axios', () => ({}))

import DeGrid from '../DeGrid.vue'

describe('DeGrid', () => {
  it('renders SVG with grid patterns', () => {
    const wrapper = shallowMount(DeGrid, {
      props: {
        matrixStyle: { width: 10, height: 10 }
      }
    })
    expect(wrapper.find('svg').exists()).toBe(true)
    expect(wrapper.find('svg defs').exists()).toBe(true)
  })

  it('computes grid dimensions from matrixStyle', () => {
    const wrapper = shallowMount(DeGrid, {
      props: {
        matrixStyle: { width: 20, height: 15 }
      }
    })
    // Verify SVG renders with computed grid patterns
    const patterns = wrapper.findAll('pattern')
    expect(patterns.length).toBe(3) // smallGrid, middleGrid, grid
  })

  it('accepts themes prop', () => {
    const wrapper = shallowMount(DeGrid, {
      props: {
        matrixStyle: { width: 10, height: 10 },
        themes: 'light'
      }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
