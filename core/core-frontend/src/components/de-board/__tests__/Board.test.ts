import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

vi.mock('@/utils/propTypes', () => ({
  propTypes: {
    string: {
      def: vi.fn((v: string) => v)
    }
  }
}))

import Board from '../Board.vue'

describe('Board', () => {
  it('should render with valid board name', () => {
    const wrapper = shallowMount(Board, {
      props: { name: 'board_1', className: 'test-border' }
    })
    expect(wrapper.find('.svg-container').exists()).toBe(true)
  })

  it('should render empty div for unknown board name', () => {
    const wrapper = shallowMount(Board, {
      props: { name: 'unknown_board' }
    })
    expect(wrapper.find('.svg-container').exists()).toBe(true)
  })

  it('should render all board types without error', () => {
    const boardNames = ['board_1', 'board_2', 'board_3', 'board_4', 'board_5', 'board_6', 'board_7', 'board_8', 'board_9']
    boardNames.forEach(name => {
      const wrapper = shallowMount(Board, {
        props: { name }
      })
      expect(wrapper.find('.svg-container').exists()).toBe(true)
    })
  })
})
