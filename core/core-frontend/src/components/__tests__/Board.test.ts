import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import Board from '@/components/de-board/Board.vue'

describe('Board', () => {
  it('renders svg markup for a known board name', () => {
    const wrapper = mount(Board, { props: { name: 'board_1' } })

    expect(wrapper.html()).toContain('<svg')
    expect(wrapper.html()).toContain('p-id="2688"')
  })

  it('updates rendered markup when the board name changes', async () => {
    const wrapper = mount(Board, { props: { name: 'board_1' } })

    await wrapper.setProps({ name: 'board_5' })

    expect(wrapper.html()).toContain('p-id="3461"')
  })

  it('renders empty content for an unknown board name', () => {
    const wrapper = mount(Board, { props: { name: 'missing' } })

    expect(wrapper.get('.svg-container').html()).not.toContain('<svg')
  })
})
