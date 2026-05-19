import { describe, expect, it } from 'vitest'

import '../DateUtil'

type FormattableDate = Date & { format: (fmt?: string) => string }

const format = (date: Date, fmt?: string) => (date as FormattableDate).format(fmt)

describe('DateUtil', () => {
  it('formats dates with the default pattern when no fmt is provided', () => {
    const date = new Date(2024, 0, 2, 3, 4, 5)

    expect(format(date)).toBe('2024-01-02 03:04:05')
  })

  it('supports zero-padded date and time tokens', () => {
    const date = new Date(2024, 8, 9, 7, 6, 5)

    expect(format(date, 'yyyy-MM-dd hh:mm:ss')).toBe('2024-09-09 07:06:05')
  })

  it('supports localized literals and short year tokens', () => {
    const date = new Date(2024, 10, 3, 0, 0, 0)

    expect(format(date, 'yy年M月d日')).toBe('24年11月3日')
    expect(format(date, 'yyyy年')).toBe('2024年')
  })

  it('supports quarter and millisecond tokens', () => {
    const date = new Date(2024, 4, 1, 8, 0, 0, 123)

    expect(format(date, 'yyyy-q-S')).toBe('2024-2-123')
  })
})
