import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/components/icon-group/board-list', () => ({
  iconBoardMap: {
    alpha: defineComponent({
      name: 'AlphaBoard',
      template: '<svg class="alpha-board"></svg>'
    }),
    beta: defineComponent({
      name: 'BetaBoard',
      template: '<svg class="beta-board"></svg>'
    })
  }
}))

vi.mock('@/components/icon-custom', () => ({
  Icon: defineComponent({
    name: 'Icon',
    template: '<span class="icon-stub"><slot /></span>'
  })
}))

import BorderOptionPrefix from '@/components/visualization/component-background/BorderOptionPrefix.vue'

describe('BorderOptionPrefix', () => {
  it('renders the icon resolved from the transformed board url', () => {
    const wrapper = mount(BorderOptionPrefix, {
      props: {
        url: 'board/alpha.svg',
        innerImageColor: '#123456'
      }
    })

    expect(wrapper.find('.alpha-board').exists()).toBe(true)
  })

  it('passes the configured image color into the icon style', () => {
    const wrapper = mount(BorderOptionPrefix, {
      props: {
        url: 'board/alpha.svg',
        innerImageColor: '#123456'
      }
    })

    expect(wrapper.find('.svg-background').attributes('style')).toContain('color: #123456;')
  })

  it('switches to a different icon when the board url changes', () => {
    const wrapper = mount(BorderOptionPrefix, {
      props: {
        url: 'board/beta.svg',
        innerImageColor: '#abcdef'
      }
    })

    expect(wrapper.find('.beta-board').exists()).toBe(true)
  })
})
