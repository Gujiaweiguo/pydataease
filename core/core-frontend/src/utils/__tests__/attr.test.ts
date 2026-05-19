import { describe, expect, it } from 'vitest'

import {
  borderStyleOptions,
  fieldType,
  fieldTypeText,
  horizontalPosition,
  multiDimensionalData,
  optionMap,
  positionData,
  selectKey,
  styleData,
  styleMap,
  textAlignOptions,
  verticalAlignOptions
} from '../attr'

describe('attr', () => {
  it('exports ordered position metadata with expected numeric constraints', () => {
    expect(positionData).toEqual([
      { key: 'left', label: 'X', min: -1000, max: 20000, step: 1 },
      { key: 'width', label: 'W', min: 2, max: 20000, step: 1 },
      { key: 'top', label: 'Y', min: -1000, max: 20000, step: 1 },
      { key: 'height', label: 'H', min: 2, max: 20000, step: 1 }
    ])
    expect(multiDimensionalData.map(item => item.key)).toEqual(['x', 'y', 'z'])
    expect(multiDimensionalData.every(item => item.min === -360 && item.max === 360)).toBe(true)
  })

  it('contains key style controls with matching labels and step rules', () => {
    const opacity = styleData.find(item => item.key === 'opacity')
    const fontWeight = styleData.find(item => item.key === 'fontWeight')
    const borderStyle = styleData.find(item => item.key === 'borderStyle')

    expect(opacity).toEqual({ key: 'opacity', label: '不透明度', min: 0, max: 1, step: 0.1 })
    expect(fontWeight).toEqual({
      key: 'fontWeight',
      label: '字体粗细',
      min: 100,
      max: 900,
      step: 100
    })
    expect(borderStyle).toEqual({ key: 'borderStyle', label: '边框风格' })
  })

  it('exposes style labels and option maps for selectable keys', () => {
    expect(styleMap.left).toBe('x 坐标')
    expect(styleMap.opacity).toBe('不透明度')
    expect(selectKey).toEqual(['textAlign', 'borderStyle', 'verticalAlign'])
    expect(horizontalPosition).toEqual(['headHorizontalPosition'])
    expect(optionMap).toEqual({
      textAlign: textAlignOptions,
      borderStyle: borderStyleOptions,
      verticalAlign: verticalAlignOptions
    })
  })

  it('keeps field types and display text aligned for index-based lookup', () => {
    expect(fieldType).toHaveLength(fieldTypeText.length)
    expect(fieldType[0]).toBe('text')
    expect(fieldTypeText[0]).toBe('文本')
    expect(fieldType[5]).toBe('location')
    expect(fieldTypeText[5]).toBe('地理位置')
    expect(fieldType.at(-1)).toBe('url')
    expect(fieldTypeText.at(-1)).toBe('URL')
  })
})
