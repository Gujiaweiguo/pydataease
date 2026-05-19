import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/config/axios', () => ({}))
vi.mock('@/components/icon-group/chart-list-empty', () => ({
  iconChartMap: { line: { template: '<span>light</span>' } }
}))
vi.mock('@/components/icon-group/chart-dark-list-empty', () => ({
  iconChartDarkMap: { 'line-dark': { template: '<span>dark</span>' } }
}))

import ChartEmptyInfo from '../ChartEmptyInfo.vue'

const mountComponent = (themes = 'light', viewIcon = 'line') =>
  shallowMount(ChartEmptyInfo, {
    props: { themes, viewIcon },
    global: {
      stubs: {
        Icon: { template: '<div class="icon-wrapper"><slot /></div>' }
      }
    }
  })

describe('ChartEmptyInfo', () => {
  it('renders without errors for light theme', () => {
    const wrapper = mountComponent('light', 'line')
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.icon-wrapper').exists()).toBe(true)
  })

  it('renders without errors for dark theme', () => {
    const wrapper = mountComponent('dark', 'line')
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.icon-wrapper').exists()).toBe(true)
  })

  it('re-renders when theme prop changes', async () => {
    const wrapper = mountComponent('light', 'line')
    await wrapper.setProps({ themes: 'dark' })
    expect(wrapper.exists()).toBe(true)
  })
})
