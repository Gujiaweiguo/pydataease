import { describe, expect, it } from 'vitest'

import { parseUrl } from '../ParseUrl'

describe('parseUrl', () => {
  it('parses hash paths with multiple query params', () => {
    expect(parseUrl('#/dashboard?key=val&foo=bar')).toEqual({
      path: 'dashboard',
      query: { key: 'val', foo: 'bar' }
    })
  })

  it('parses a single query param', () => {
    expect(parseUrl('#/page?a=1')).toEqual({
      path: 'page',
      query: { a: '1' }
    })
  })

  it('parses multiple query params in order', () => {
    expect(parseUrl('#/page?a=1&b=2&c=3')).toEqual({
      path: 'page',
      query: { a: '1', b: '2', c: '3' }
    })
  })

  it('keeps empty values and lets later duplicate keys win', () => {
    expect(parseUrl('#/filters?a=&a=2')).toEqual({
      path: 'filters',
      query: { a: '2' }
    })
  })

  it('throws when the hash url does not include query params', () => {
    expect(() => parseUrl('#/about')).toThrow()
  })

  it('throws for an empty hash string', () => {
    expect(() => parseUrl('')).toThrow()
  })
})
