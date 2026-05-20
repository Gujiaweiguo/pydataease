import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import SvgTriangleComponent from '../Component.vue'

const createElement = () => ({
  propValue: null,
  style: {
    width: 200,
    height: 100,
    borderColor: '#000000',
    backgroundColor: '#ff0000',
    borderActive: true,
    borderWidth: 2
  }
})

const mountComponent = () =>
  mount(SvgTriangleComponent, {
    props: {
      propValue: '',
      element: createElement()
    }
  })

describe('svg-triangle/Component', () => {
  it('renders the svg container', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('.svg-triangle-container').exists()).toBe(true)
  })

  it('renders an SVG element', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('svg').exists()).toBe(true)
  })

  it('renders a polygon element', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('polygon').exists()).toBe(true)
  })

  it('accepts propValue prop', () => {
    const wrapper = mountComponent()
    expect(wrapper.props('propValue')).toBe('')
  })

  it('accepts element prop with style', () => {
    const wrapper = mountComponent()
    expect(wrapper.props('element').style.width).toBe(200)
    expect(wrapper.props('element').style.height).toBe(100)
  })

  it('computes points via draw function', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any
    expect(vm.points).toBeTruthy()
  })

  it('applies border and fill styles from element', () => {
    const wrapper = mountComponent()
    const polygon = wrapper.find('polygon')
    expect(polygon.attributes('stroke')).toBe('#000000')
    expect(polygon.attributes('fill')).toBe('#ff0000')
  })
})
