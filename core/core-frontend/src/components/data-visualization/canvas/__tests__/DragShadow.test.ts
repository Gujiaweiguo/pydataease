import { shallowMount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import DragShadow from '../DragShadow.vue'

const mountComponent = (props: Record<string, unknown> = {}) =>
  shallowMount(DragShadow, {
    props: {
      baseWidth: 20,
      baseHeight: 30,
      curGap: 4,
      element: { x: 2, y: 3, sizeX: 4, sizeY: 5 },
      ...props
    }
  })

describe('DragShadow', () => {
  it('computes width, height and position styles from props', () => {
    const wrapper = mountComponent()
    const style = wrapper.get('.shadow-main').attributes('style')

    expect(style).toContain('padding: 4px;')
    expect(style).toContain('width: 80px;')
    expect(style).toContain('height: 150px;')
    expect(style).toContain('left: 20px;')
    expect(style).toContain('top: 57px;')
  })

  it('renders the shadow background node', () => {
    const wrapper = mountComponent()

    expect(wrapper.find('.shadow-background').exists()).toBe(true)
  })

  it('reacts to updated element coordinates and span', async () => {
    const wrapper = mountComponent()

    await wrapper.setProps({
      element: { x: 1, y: 1, sizeX: 2, sizeY: 2 }
    })

    const style = wrapper.get('.shadow-main').attributes('style')
    expect(style).toContain('width: 40px;')
    expect(style).toContain('height: 60px;')
    expect(style).toContain('left: 0px;')
    expect(style).toContain('top: -3px;')
  })
})
