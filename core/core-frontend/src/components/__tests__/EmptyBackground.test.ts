import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import EmptyBackground from '../empty-background/src/EmptyBackground.vue'

const ElEmptyStub = defineComponent({
  name: 'ElEmpty',
  props: {
    imageSize: {
      type: Number,
      default: 0
    },
    description: {
      type: String,
      default: ''
    },
    image: {
      type: String,
      default: ''
    }
  },
  template:
    '<div class="el-empty-stub"><span class="image-size">{{ imageSize }}</span><span class="description">{{ description }}</span><span class="image">{{ image }}</span><slot /></div>'
})

describe('EmptyBackground', () => {
  it('passes description and image size props to ElEmpty', () => {
    const wrapper = mount(EmptyBackground, {
      props: {
        description: 'No data available',
        imageSize: 188
      },
      global: {
        stubs: {
          ElEmpty: ElEmptyStub
        }
      }
    })

    const empty = wrapper.getComponent(ElEmptyStub)

    expect(empty.props('description')).toBe('No data available')
    expect(empty.props('imageSize')).toBe(188)
  })

  it('maps different imgType values to different image assets', () => {
    const tableWrapper = mount(EmptyBackground, {
      global: {
        stubs: {
          ElEmpty: ElEmptyStub
        }
      }
    })
    const errorWrapper = mount(EmptyBackground, {
      props: {
        imgType: 'error'
      },
      global: {
        stubs: {
          ElEmpty: ElEmptyStub
        }
      }
    })

    expect(tableWrapper.getComponent(ElEmptyStub).props('image')).toBeTruthy()
    expect(errorWrapper.getComponent(ElEmptyStub).props('image')).toBeTruthy()
    expect(errorWrapper.getComponent(ElEmptyStub).props('image')).not.toBe(
      tableWrapper.getComponent(ElEmptyStub).props('image')
    )
  })

  it('renders slot content inside ElEmpty', () => {
    const wrapper = mount(EmptyBackground, {
      global: {
        stubs: {
          ElEmpty: ElEmptyStub
        }
      },
      slots: {
        default: '<button class="retry-button">Retry</button>'
      }
    })

    expect(wrapper.find('.retry-button').exists()).toBe(true)
  })
})
