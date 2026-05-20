import { describe, it, expect } from 'vitest'

import * as mod from '../Types'

describe('Types', () => {
  it('exports BackgroundType as a type (no runtime value)', () => {
    // Type exports are erased at runtime; just verify the module is importable
    expect(mod).toBeDefined()
  })

  it('module exports no runtime values (pure type module)', () => {
    const keys = Object.keys(mod)
    expect(keys).toHaveLength(0)
  })
})
