import { describe, expect, it } from 'vitest'

import { transDateFormat, transDatePickerType } from '../DateFormatUtil'

describe('DateFormatUtil', () => {
  it.each([
    ['y', 'date_normal', 'YYYY'],
    ['y_M', 'date_normal', 'YYYY-MM'],
    ['y_M', 'date_split', 'YYYY/MM'],
    ['y_M_d', 'date_normal', 'YYYY-MM-DD'],
    ['y_M_d_H', 'date_normal', 'YYYY-MM-DD HH'],
    ['y_M_d_H_m', 'date_normal', 'YYYY-MM-DD HH:mm'],
    ['y_M_d_H_m_s', 'date_normal', 'YYYY-MM-DD HH:mm:ss'],
    ['H_m_s', 'date_normal', 'HH:mm:ss']
  ])('transDateFormat(%s, %s) returns %s', (dateStyle, datePattern, expected) => {
    expect(transDateFormat(dateStyle, datePattern)).toBe(expected)
  })

  it('falls back to the default datetime format when dateStyle is empty', () => {
    expect(transDateFormat('', 'date_split')).toBe('YYYY-MM-DD HH:mm:ss')
  })

  it('falls back to the default datetime format for unknown styles', () => {
    expect(transDateFormat('unknown', 'date_split')).toBe('YYYY-MM-DD HH:mm:ss')
  })

  it.each([
    ['y', 'year'],
    ['y_M', 'month'],
    ['y_M_d', 'date'],
    ['y_M_d_H', 'datetime'],
    ['y_M_d_H_m', 'datetime'],
    ['y_M_d_H_m_s', 'datetime']
  ])('transDatePickerType(%s) returns %s', (dateStyle, expected) => {
    expect(transDatePickerType(dateStyle)).toBe(expected)
  })

  it('returns datetime for empty or unknown picker styles', () => {
    expect(transDatePickerType(undefined)).toBe('datetime')
    expect(transDatePickerType('H_m_s')).toBe('datetime')
    expect(transDatePickerType('unknown')).toBe('datetime')
  })
})
