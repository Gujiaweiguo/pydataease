import { describe, expect, it } from 'vitest'

import { EMAIL_REGEX, PHONE_REGEX, isExternal, validUsername } from '../validate'

describe('validate utils', () => {
  it.each([
    ['https://x.com', true],
    ['http://x.com', true],
    ['mailto:a@b', true],
    ['tel:123', true],
    ['/api/pluginCommon/staticInfo', true],
    ['/api/pluginCommon/staticInfo/detail', true],
    ['/dashboard', false],
    ['ftp://x.com', false]
  ])('isExternal(%s) returns %s', (path, expected) => {
    expect(isExternal(path)).toBe(expected)
  })

  it.each([
    ['admin', true],
    ['cyw', true],
    ['other', false],
    [' admin ', true],
    [' cyw ', true]
  ])('validUsername(%s) returns %s', (value, expected) => {
    expect(validUsername(value)).toBe(expected)
  })

  it('matches valid phone numbers with PHONE_REGEX', () => {
    expect(new RegExp(PHONE_REGEX).test('13812345678')).toBe(true)
    expect(new RegExp(PHONE_REGEX).test('15700000000')).toBe(true)
  })

  it('rejects invalid phone numbers with PHONE_REGEX', () => {
    expect(new RegExp(PHONE_REGEX).test('12812345678')).toBe(false)
    expect(new RegExp(PHONE_REGEX).test('1381234567')).toBe(false)
  })

  it('matches valid email addresses with EMAIL_REGEX', () => {
    expect(new RegExp(EMAIL_REGEX).test('user.name_01@test-mail.com')).toBe(true)
    expect(new RegExp(EMAIL_REGEX).test('a_b.c@demo.cn')).toBe(true)
  })

  it('rejects invalid email addresses with EMAIL_REGEX', () => {
    expect(new RegExp(EMAIL_REGEX).test('invalid-email')).toBe(false)
    expect(new RegExp(EMAIL_REGEX).test('a@b')).toBe(false)
  })
})
