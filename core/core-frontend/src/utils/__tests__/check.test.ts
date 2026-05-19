import { describe, expect, it } from 'vitest'

import checkArrayRepeat from '../check'

describe('checkArrayRepeat', () => {
  it('returns true when duplicate names exist', () => {
    expect(
      checkArrayRepeat(
        [
          { name: 'a' },
          { name: 'a' }
        ],
        'name'
      )
    ).toBe(true)
  })

  it('returns false when all names are unique', () => {
    expect(
      checkArrayRepeat(
        [
          { name: 'a' },
          { name: 'b' }
        ],
        'name'
      )
    ).toBe(false)
  })

  it('returns false for an empty array', () => {
    expect(checkArrayRepeat([], 'name')).toBe(false)
  })

  it('returns false for a single-item array', () => {
    expect(checkArrayRepeat([{ name: 'a' }], 'name')).toBe(false)
  })

  it('supports non-string keys such as numeric ids', () => {
    expect(
      checkArrayRepeat(
        [
          { id: 1 },
          { id: 1 },
          { id: 2 }
        ],
        'id'
      )
    ).toBe(true)
  })
})
