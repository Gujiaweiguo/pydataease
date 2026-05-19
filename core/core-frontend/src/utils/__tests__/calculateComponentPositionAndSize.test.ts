import { describe, expect, it, vi } from 'vitest'

vi.mock('@/utils/translate', () => ({
  calculateRotatedPointCoordinate: (point, center, rotate) => {
    const radian = (rotate * Math.PI) / 180
    return {
      x:
        (point.x - center.x) * Math.cos(radian) - (point.y - center.y) * Math.sin(radian) + center.x,
      y:
        (point.x - center.x) * Math.sin(radian) + (point.y - center.y) * Math.cos(radian) + center.y
    }
  },
  getCenterPoint: (p1, p2) => ({
    x: p1.x + (p2.x - p1.x) / 2,
    y: p1.y + (p2.y - p1.y) / 2
  })
}))

import calculateComponentPositionAndSize, {
  calculateRadioComponentPositionAndSize
} from '../calculateComponentPositionAndSize'

describe('calculateComponentPositionAndSize', () => {
  it('resizes from the right handle without locked proportions', () => {
    const style = { width: 100, height: 50, left: 10, top: 20, rotate: 0 }

    calculateComponentPositionAndSize(
      'r',
      style,
      { x: 160, y: 45 },
      2,
      false,
      {
        symmetricPoint: { x: 10, y: 45 },
        curPoint: { x: 110, y: 45 }
      }
    )

    expect(style).toMatchObject({ width: 150, height: 50, left: 10, top: 20 })
  })

  it('resizes from the bottom handle with locked proportions', () => {
    const style = { width: 100, height: 50, left: 10, top: 20, rotate: 0 }

    calculateComponentPositionAndSize(
      'b',
      style,
      { x: 60, y: 100 },
      2,
      true,
      {
        symmetricPoint: { x: 60, y: 20 },
        curPoint: { x: 60, y: 70 }
      }
    )

    expect(style).toMatchObject({ width: 160, height: 80, left: -20, top: 20 })
  })

  it('resizes from the right handle with locked proportions', () => {
    const style = { width: 100, height: 50, left: 10, top: 20, rotate: 0 }

    calculateComponentPositionAndSize(
      'r',
      style,
      { x: 160, y: 45 },
      2,
      true,
      {
        symmetricPoint: { x: 10, y: 45 },
        curPoint: { x: 110, y: 45 }
      }
    )

    expect(style).toMatchObject({ width: 150, height: 75, left: 10, top: 8 })
  })

  it('positions radio components on the top and left edges', () => {
    const topStyle = { width: 40, height: 20, left: 0, top: 0 }
    const leftStyle = { width: 40, height: 20, left: 0, top: 0 }

    calculateRadioComponentPositionAndSize('t', topStyle as any, { x: 100, y: 80 })
    calculateRadioComponentPositionAndSize('l', leftStyle as any, { x: 100, y: 80 })

    expect(topStyle).toMatchObject({ left: 80, top: 60 })
    expect(leftStyle).toMatchObject({ left: 60, top: 70 })
  })

  it('positions radio components on corner handles', () => {
    const ltStyle = { width: 40, height: 20, left: 0, top: 0 }
    const rbStyle = { width: 40, height: 20, left: 0, top: 0 }

    calculateRadioComponentPositionAndSize('lt', ltStyle as any, { x: 100, y: 80 })
    calculateRadioComponentPositionAndSize('rb', rbStyle as any, { x: 100, y: 80 })

    expect(ltStyle).toMatchObject({ left: 60, top: 60 })
    expect(rbStyle).toMatchObject({ left: 100, top: 80 })
  })

  it('does nothing for unknown radio handles', () => {
    const style = { width: 40, height: 20, left: 5, top: 6 }

    calculateRadioComponentPositionAndSize('unknown', style as any, { x: 100, y: 80 })

    expect(style).toMatchObject({ width: 40, height: 20, left: 5, top: 6 })
  })
})
