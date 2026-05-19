import { describe, expect, it } from 'vitest'

import { reverseColor } from '../util'

describe('views util', () => {
  it.each([
    ['#000000', '#ffffff'],
    ['#FFFFFF', '#000000'],
    ['#123456', '#edcba9'],
    ['123456', '#edcba9'],
    ['#abc', '#fff543'],
    ['#fff', '#fff000']
  ])('reverseColor(%s) returns %s', (input, expected) => {
    expect(reverseColor(input)).toBe(expected)
  })
})
