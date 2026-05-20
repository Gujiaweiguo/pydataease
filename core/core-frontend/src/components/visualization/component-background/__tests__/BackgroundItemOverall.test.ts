import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const utilMock = vi.hoisted(() => ({
  hexColorToRGBA: vi.fn(() => 'rgba(17, 34, 51, 0.4)')
}))

vi.mock('@/views/chart/components/js/util', () => ({
  hexColorToRGBA: utilMock.hexColorToRGBA
}))

vi.mock('@/components/icon-group/board-list', () => ({
  iconBoardMap: {
    star: defineComponent({ name: 'StarIcon', template: '<svg class="star-icon"></svg>' })
  }
}))

import BackgroundItemOverall from '../BackgroundItemOverall.vue'

const mountComponent = (commonBackground?: Record<string, unknown>) =>
  mount(BackgroundItemOverall, {
    props: {
      template: { name: 'Star Board', url: 'board/star.svg' },
      commonBackground: {
        innerImage: 'board/star.svg',
        backgroundColorSelect: true,
        color: '#112233',
        alpha: 40,
        innerImageColor: '#ff0000',
        ...commonBackground
      }
    },
    global: {
      stubs: {
        Icon: defineComponent({ name: 'Icon', template: '<span class="icon-stub"><slot /></span>' })
      }
    }
  })

describe('BackgroundItemOverall', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders template name and active class for selected image', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('Star Board')
    expect(wrapper.get('.template-img').classes()).toContain('template-img-active')
  })

  it('applies rgba background style when color selection is enabled', () => {
    const wrapper = mountComponent()

    expect(wrapper.get('.template-img').attributes('style')).toContain(
      'background-color: rgba(17, 34, 51, 0.4)'
    )
    expect(utilMock.hexColorToRGBA).toHaveBeenCalledWith('#112233', 40)
  })

  it('updates background image and emits border change on click', async () => {
    const wrapper = mountComponent({ innerImage: 'board/other.svg' })

    await wrapper.get('.template-img').trigger('click')

    const props = wrapper.props() as { commonBackground: { innerImage: string } }
    expect(props.commonBackground.innerImage).toBe('board/star.svg')
    expect(wrapper.emitted('borderChange')).toEqual([[]])
  })
})
