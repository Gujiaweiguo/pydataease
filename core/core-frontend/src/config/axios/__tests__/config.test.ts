import { describe, expect, it } from 'vitest'
import { config } from '../config'

describe('axios config', () => {
  it('exports config object with correct base_url structure', () => {
    expect(config).toBeDefined()
    expect(config.base_url).toBeDefined()
    expect(config.base_url).toEqual({
      base: '',
      dev: '',
      pro: '',
      test: ''
    })
  })

  it('has result_code set to 0', () => {
    expect(config.result_code).toBe(0)
  })

  it('has default_headers set to application/json', () => {
    expect(config.default_headers).toBe('application/json')
  })

  it('has request_timeout set to 60000', () => {
    expect(config.request_timeout).toBe(60000)
  })

  it('has all expected top-level keys', () => {
    expect(Object.keys(config)).toEqual(
      expect.arrayContaining(['base_url', 'result_code', 'default_headers', 'request_timeout'])
    )
  })
})
