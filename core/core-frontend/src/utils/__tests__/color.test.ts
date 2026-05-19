import { describe, expect, it } from 'vitest'

import { colorStringToHex } from '../color'

describe('color utils', () => {
  it.each([
    ['rgb(255,0,0)', '#FF0000'],
    ['rgb(0,255,0)', '#00FF00'],
    ['rgba(0,0,255,0.5)', '#0000FF80'],
    ['rgb( 12 , 34 , 56 )', '#0C2238'],
    ['rgba(255,255,255,2)', '#FFFFFFFF'],
    ['rgb(300,256,999)', '#FFFFFF']
  ])('colorStringToHex(%s) returns %s', (input, expected) => {
    expect(colorStringToHex(input)).toBe(expected)
  })

  it('returns null for invalid color strings', () => {
    expect(colorStringToHex('invalid')).toBeNull()
    expect(colorStringToHex('transparent')).toBeNull()
    expect(colorStringToHex('#FF0000')).toBeNull()
  })
})
