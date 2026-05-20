import { shallowMount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import RectShapeComponent from '../Component.vue'

describe('rect-shape/Component', () => {
  it('renders the root container', () => {
    const wrapper = shallowMount(RectShapeComponent, {
      props: {
        propValue: '',
        element: { propValue: null }
      }
    })
    expect(wrapper.find('.circle-shape').exists()).toBe(true)
  })

  it('accepts propValue prop', () => {
    const wrapper = shallowMount(RectShapeComponent, {
      props: {
        propValue: 'test value',
        element: { propValue: null }
      }
    })
    expect(wrapper.props('propValue')).toBe('test value')
  })

  it('accepts element prop', () => {
    const element = { propValue: null, id: 'rect-1' }
    const wrapper = shallowMount(RectShapeComponent, {
      props: {
        propValue: '',
        element
      }
    })
    expect(wrapper.props('element')).toEqual(element)
  })
})
