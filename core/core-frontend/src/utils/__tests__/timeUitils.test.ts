import { describe, expect, it } from 'vitest'

import { getRange, getTimeBegin } from '../timeUitils'

describe('timeUitils', () => {
  const timestamp = new Date(2024, 4, 15, 13, 45, 20).getTime()

  it('returns the raw selection when the date is invalid', () => {
    expect(getRange('not-a-date', 'y_M_d_H')).toBe('not-a-date:')
    expect(getRange('still-invalid', 'month')).toBe('still-invalid')
  })

  it('calculates full-year ranges from a timestamp', () => {
    expect(getRange(timestamp, 'year')).toEqual([
      +new Date(2024, 0, 1),
      +new Date(2024, 11, 31) + 24 * 60 * 60 * 1000 - 1000
    ])
  })

  it('calculates month ranges using the month boundaries of the selected date', () => {
    expect(getRange(timestamp, 'month')).toEqual([
      +new Date(2024, 4, 1),
      +new Date(2024, 5, 1) - 1000
    ])
  })

  it('calculates hour, minute, and second windows with the expected durations', () => {
    const hourRange = getRange(timestamp, 'hour') as number[]
    const minuteRange = getRange(timestamp, 'minute') as number[]
    const secondRange = getRange(timestamp, 'y_M_d_H_m_s') as number[]

    expect(hourRange[0]).toBe(timestamp)
    expect(hourRange[1] - hourRange[0]).toBe(60 * 60 * 1000 - 1000)
    expect(minuteRange[1] - minuteRange[0]).toBe(60 * 1000 - 1000)
    expect(secondRange[1] - secondRange[0]).toBe(999)
  })

  it('returns a point range for datetime granularity', () => {
    expect(getRange(timestamp, 'datetime')).toEqual([timestamp, timestamp])
  })

  it('uses matching range helpers for supported begin granularities and falls back otherwise', () => {
    expect(getTimeBegin(timestamp, 'year')).toEqual(getRange(timestamp, 'year'))
    expect(getTimeBegin(timestamp, 'month')).toEqual(getRange(timestamp, 'month'))
    expect(getTimeBegin(timestamp, 'custom')).toBe(timestamp)
  })
})
