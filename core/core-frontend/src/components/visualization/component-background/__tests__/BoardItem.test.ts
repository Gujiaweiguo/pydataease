import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/components/icon-group/board-list', () => ({
  iconBoardMap: {
    star: defineComponent({ name: 'StarIcon', template: '<svg class="star-icon"></svg>' })
  }
}))

import BoardItem from '../BoardItem.vue'

const mountComponent = (active = false, themes: 'dark' | 'light' = 'dark') =>
  mount(BoardItem, {
    props: {
      item: { name: 'Star Board', url: 'board/star.svg' },
      active,
      themes,
      innerImageColor: '#ff0000'
    },
    global: {
      stubs: {
        Icon: defineComponent({ name: 'Icon', template: '<span class="icon-stub"><slot /></span>' })
      }
    }
  })

describe('BoardItem', () => {
  it('renders item name', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('Star Board')
  })

  it('applies selected-active class when active prop is true', () => {
    const wrapper = mountComponent(true)

    expect(wrapper.find('.icon-area').classes()).toContain('selected-active')
  })

  it('does not apply selected-active class when active prop is false', () => {
    const wrapper = mountComponent(false)

    expect(wrapper.find('.icon-area').classes()).not.toContain('selected-active')
  })

  it('applies icon-area-dark class when themes is dark', () => {
    const wrapper = mountComponent(false, 'dark')

    expect(wrapper.find('.icon-area').classes()).toContain('icon-area-dark')
  })

  it('does not apply icon-area-dark class when themes is light', () => {
    const wrapper = mountComponent(false, 'light')

    expect(wrapper.find('.icon-area').classes()).not.toContain('icon-area-dark')
  })
})
