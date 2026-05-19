import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/components/icon-group/board-list', () => ({
  iconBoardMap: {
    star: defineComponent({
      name: 'StarBoard',
      template: '<svg class="star-board"></svg>'
    })
  }
}))

import BoardItem from '@/components/visualization/component-background/BoardItem.vue'

const mountComponent = (props: Record<string, unknown> = {}) =>
  mount(BoardItem, {
    props: {
      item: { name: 'Star', url: 'board/star.svg' },
      active: false,
      innerImageColor: '#3370ff',
      ...props
    },
    global: {
      stubs: {
        Icon: defineComponent({
          name: 'Icon',
          template: '<span class="icon-stub"><slot /></span>'
        })
      }
    }
  })

describe('BoardItem', () => {
  it('renders the icon label and forwards the icon color', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('Star')
    expect(wrapper.find('.svg-background').attributes('style')).toContain('color: #3370ff;')
  })

  it('applies the active selection class when active is true', () => {
    const wrapper = mountComponent({ active: true })

    expect(wrapper.get('.icon-area').classes()).toContain('selected-active')
  })

  it('uses the dark background class by default and skips it for light themes', () => {
    const darkWrapper = mountComponent()
    const lightWrapper = mountComponent({ themes: 'light' })

    expect(darkWrapper.get('.icon-area').classes()).toContain('icon-area-dark')
    expect(lightWrapper.get('.icon-area').classes()).not.toContain('icon-area-dark')
  })
})
