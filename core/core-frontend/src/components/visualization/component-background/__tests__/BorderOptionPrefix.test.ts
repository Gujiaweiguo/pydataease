import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/components/icon-group/board-list', () => ({
  iconBoardMap: {
    star: defineComponent({ name: 'StarIcon', template: '<svg class="star-icon"></svg>' })
  }
}))

vi.mock('@/components/icon-custom', () => ({
  Icon: defineComponent({ name: 'Icon', template: '<span class="icon-stub"><slot /></span>' })
}))

import BorderOptionPrefix from '../BorderOptionPrefix.vue'

const mountComponent = (url = 'board/star.svg', innerImageColor = '#ff0000') =>
  mount(BorderOptionPrefix, {
    props: { url, innerImageColor }
  })

describe('BorderOptionPrefix', () => {
  it('renders the icon container', () => {
    const wrapper = mountComponent()

    expect(wrapper.find('.img-option-prefix').exists()).toBe(true)
  })

  it('renders with different url values', () => {
    const wrapper = mountComponent('board/board_1.svg', '#00ff00')

    expect(wrapper.find('.img-option-prefix').exists()).toBe(true)
  })
})
