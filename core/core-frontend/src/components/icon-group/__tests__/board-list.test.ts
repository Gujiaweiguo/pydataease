import { describe, it, expect, vi } from 'vitest'

vi.mock('@/assets/svg/board_1.svg', () => ({ default: 'board_1.svg' }))
vi.mock('@/assets/svg/board_2.svg', () => ({ default: 'board_2.svg' }))
vi.mock('@/assets/svg/board_3.svg', () => ({ default: 'board_3.svg' }))
vi.mock('@/assets/svg/board_4.svg', () => ({ default: 'board_4.svg' }))
vi.mock('@/assets/svg/board_5.svg', () => ({ default: 'board_5.svg' }))
vi.mock('@/assets/svg/board_6.svg', () => ({ default: 'board_6.svg' }))
vi.mock('@/assets/svg/board_7.svg', () => ({ default: 'board_7.svg' }))
vi.mock('@/assets/svg/board_8.svg', () => ({ default: 'board_8.svg' }))
vi.mock('@/assets/svg/board_9.svg', () => ({ default: 'board_9.svg' }))

import * as mod from '../board-list'

describe('board-list', () => {
  it('exports iconBoardMap', () => {
    expect(mod.iconBoardMap).toBeDefined()
    expect(typeof mod.iconBoardMap).toBe('object')
  })

  it('contains all 9 board entries', () => {
    expect(Object.keys(mod.iconBoardMap)).toHaveLength(9)
  })

  it('has keys board_1 through board_9', () => {
    for (let i = 1; i <= 9; i++) {
      expect(mod.iconBoardMap).toHaveProperty(`board_${i}`)
    }
  })

  it('each entry maps to a string value', () => {
    Object.values(mod.iconBoardMap).forEach(val => {
      expect(typeof val).toBe('string')
    })
  })
})
