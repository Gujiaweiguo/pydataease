import { describe, it, expect, vi } from 'vitest'

vi.mock('pinia', () => ({
  storeToRefs: () => ({ dvInfo: { value: {} } })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({})
}))

vi.mock('@/api/user', () => ({
  ipInfoApi: vi.fn(() => Promise.resolve({ data: { ip: '127.0.0.1', account: 'admin', name: 'Admin', model: 'active' } }))
}))

vi.mock('@/utils/utils', () => ({
  isISOMobile: vi.fn(() => false)
}))

import { getNow } from '../watermark'

describe('watermark utilities', () => {
  describe('getNow', () => {
    it('should return formatted date string', () => {
      const result = getNow()
      const pattern = /^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/
      expect(result).toMatch(pattern)
    })

    it('should pad single digit months with zero', () => {
      const result = getNow()
      const parts = result.split('-')
      const month = parts[1]
      expect(month.length).toBe(2)
    })

    it('should pad single digit days with zero', () => {
      const result = getNow()
      const dayPart = result.split('-')[2].split(' ')[0]
      expect(dayPart.length).toBe(2)
    })
  })
})
