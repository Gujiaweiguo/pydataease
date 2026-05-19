import { shallowMount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import Area from '../Area.vue'

describe('Area', () => {
  it('renders area position and dimensions from props', () => {
    const wrapper = shallowMount(Area, {
      props: {
        start: { x: 12, y: 24 },
        width: 80,
        height: 60
      }
    })

    const style = wrapper.get('.area').attributes('style')
    expect(style).toContain('left: 12px;')
    expect(style).toContain('top: 24px;')
    expect(style).toContain('width: 80px;')
    expect(style).toContain('height: 60px;')
  })

  it('uses zero width and height by default', () => {
    const wrapper = shallowMount(Area)
    const style = wrapper.get('.area').attributes('style')

    expect(style).toContain('width: 0px;')
    expect(style).toContain('height: 0px;')
  })

  it('updates styles when the start position changes', async () => {
    const wrapper = shallowMount(Area, {
      props: {
        start: { x: 1, y: 2 },
        width: 10,
        height: 20
      }
    })

    await wrapper.setProps({ start: { x: 30, y: 40 } })

    const style = wrapper.get('.area').attributes('style')
    expect(style).toContain('left: 30px;')
    expect(style).toContain('top: 40px;')
  })
})
