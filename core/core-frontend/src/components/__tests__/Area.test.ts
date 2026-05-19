import { shallowMount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import Area from '@/components/data-visualization/canvas/Area.vue'

describe('Area', () => {
  it('renders selection styles from props', () => {
    const wrapper = shallowMount(Area, {
      props: {
        start: { x: 12, y: 24 },
        width: 80,
        height: 60
      }
    })

    const area = wrapper.get('.area')
    expect(area.attributes('style')).toContain('left: 12px;')
    expect(area.attributes('style')).toContain('top: 24px;')
    expect(area.attributes('style')).toContain('width: 80px;')
    expect(area.attributes('style')).toContain('height: 60px;')
  })

  it('uses defaults when width and height are omitted', () => {
    const wrapper = shallowMount(Area)

    expect(wrapper.get('.area').attributes('style')).toContain('width: 0px;')
    expect(wrapper.get('.area').attributes('style')).toContain('height: 0px;')
  })

  it('updates style when start coordinates change', async () => {
    const wrapper = shallowMount(Area, {
      props: {
        start: { x: 1, y: 2 },
        width: 10,
        height: 20
      }
    })

    await wrapper.setProps({ start: { x: 30, y: 40 } })

    expect(wrapper.get('.area').attributes('style')).toContain('left: 30px;')
    expect(wrapper.get('.area').attributes('style')).toContain('top: 40px;')
  })
})
