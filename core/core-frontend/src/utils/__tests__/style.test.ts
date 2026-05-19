import { beforeEach, describe, expect, it, vi } from 'vitest'

const { hexColorToRGBAMock, imgUrlTransMock, isTabCanvasMock } = vi.hoisted(() => ({
  hexColorToRGBAMock: vi.fn(),
  imgUrlTransMock: vi.fn(),
  isTabCanvasMock: vi.fn()
}))

vi.mock('@/utils/translate', () => ({
  sin: (rotate: number) => Math.abs(Math.sin((rotate * Math.PI) / 180)),
  cos: (rotate: number) => Math.abs(Math.cos((rotate * Math.PI) / 180)),
  toPercent: (value: number) => `${value * 100}%`
}))

vi.mock('@/utils/imgUtils', () => ({
  imgUrlTrans: imgUrlTransMock
}))

vi.mock('@/views/chart/components/js/util', () => ({
  hexColorToRGBA: hexColorToRGBAMock
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    dvInfo: { type: 'dashboard' },
    mobileInPc: false,
    editMode: 'edit'
  })
}))

vi.mock('@/utils/canvasUtils', () => ({
  isMainCanvas: vi.fn(() => true),
  isTabCanvas: isTabCanvasMock
}))

import {
  createGroupStyle,
  dataVTabComponentAdd,
  getComponentRotatedStyle,
  getItemAllStyle,
  getShapeItemStyle,
  getShapeStyle,
  getStyle,
  getSVGStyle,
  groupItemStyleAdaptor,
  groupStyleRevert,
  syncShapeItemStyle
} from '../style'

describe('style utils', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    isTabCanvasMock.mockReturnValue(false)
    hexColorToRGBAMock.mockReturnValue('rgba(17,34,51,0.5)')
    imgUrlTransMock.mockImplementation(url => `mock:${url}`)
  })

  it('builds absolute shape styles with px units and rotation transform', () => {
    expect(getShapeStyle({ width: 120, height: 60, top: 8, left: 16, rotate: 45 })).toEqual({
      width: '120px',
      height: '60px',
      top: '8px',
      left: '16px',
      transform: 'rotate(45deg)'
    })
  })

  it('maps dashboard, tab preview, and default item styles correctly', () => {
    expect(
      getShapeItemStyle(
        { x: 2, y: 3, sizeX: 2, sizeY: 3, isPlayer: false },
        { dvModel: 'dashboard', cellWidth: 100, cellHeight: 50, curGap: 8 }
      )
    ).toEqual({
      padding: '8px!important',
      width: '200px',
      height: '150px',
      left: '100px',
      top: '100px'
    })

    isTabCanvasMock.mockReturnValue(true)
    expect(
      getShapeItemStyle(
        {
          canvasId: 'tab-1',
          groupStyle: { width: 0.5, height: 0.25, top: 0.1, left: 0.2 },
          style: { width: 200, height: 100, top: 10, left: 20 }
        },
        { dvModel: 'dataV', cellWidth: 0, cellHeight: 0, curGap: 4, showPosition: 'preview' }
      )
    ).toEqual({
      padding: '4px!important',
      width: '50%',
      height: '25%',
      top: '10%',
      left: '20%'
    })

    isTabCanvasMock.mockReturnValue(false)
    expect(
      getShapeItemStyle(
        { style: { width: 88, height: 44, left: 11, top: 22 } },
        { dvModel: 'dataV', cellWidth: 0, cellHeight: 0, curGap: 2, showPosition: 'edit' }
      )
    ).toEqual({
      padding: '2px!important',
      width: '88px',
      height: '44px',
      left: '11px',
      top: '22px'
    })
  })

  it('syncs dashboard grid coordinates back onto component styles', () => {
    const item = {
      x: 3,
      y: 4,
      sizeX: 2,
      sizeY: 5,
      style: { left: 0, top: 0, width: 0, height: 0 }
    }

    syncShapeItemStyle(item, 50, 20)

    expect(item.style).toEqual({ left: 100, top: 60, width: 100, height: 100 })
  })

  it('applies SVG units, filtering, and transform handling', () => {
    expect(
      getSVGStyle(
        {
          opacity: 0.7,
          width: 10,
          height: 20,
          top: 5,
          left: '',
          rotate: 30,
          fontSize: 12,
          fontWeight: 600,
          lineHeight: 1.4,
          letterSpacing: 2,
          textAlign: 'center',
          color: '#fff'
        },
        ['color']
      )
    ).toEqual({
      opacity: 0.7,
      width: '10px',
      height: '20px',
      top: '5px',
      transform: 'rotate(30deg)',
      fontSize: '12px',
      fontWeight: 600,
      lineHeight: 1.4,
      letterSpacing: '2px',
      textAlign: 'center'
    })
  })

  it('merges component styles with common background images and rgba colors', () => {
    expect(
      getItemAllStyle({
        style: { width: 20, borderRadius: 3, rotate: 0, color: '#000' },
        commonBackground: {
          backgroundColorSelect: true,
          backgroundColor: '#112233',
          alpha: 0.5,
          backgroundImageEnable: true,
          backgroundType: 'outerImage',
          outerImage: '/static-resource/bg.png'
        }
      })
    ).toEqual({
      width: '20px',
      borderRadius: '3px',
      transform: 'rotate(0deg)',
      color: '#000',
      background: 'url(mock:/static-resource/bg.png) no-repeat rgba(17,34,51,0.5)'
    })
    expect(hexColorToRGBAMock).toHaveBeenCalledWith('#112233', 0.5)
  })

  it('calculates rotated bounding boxes and plain style output', () => {
    expect(getStyle({ width: 12, left: 5, rotate: 0, opacity: 1 })).toEqual({
      width: '12px',
      left: '5px',
      transform: 'rotate(0deg)',
      opacity: 1
    })

    const rotated = getComponentRotatedStyle({
      width: 100,
      height: 50,
      left: 10,
      top: 20,
      rotate: 90
    })
    expect(rotated.left).toBe(35)
    expect(rotated.top).toBe(-5)
    expect(rotated.width).toBeCloseTo(50, 10)
    expect(rotated.height).toBe(100)
    expect(rotated.right).toBe(85)
    expect(rotated.bottom).toBe(95)
    expect(rotated.rotate).toBe(90)
  })

  it('creates and restores group-relative positioning data', () => {
    const group = {
      style: { left: 10, top: 20, width: 200, height: 100 },
      propValue: [
        {
          style: { left: 60, top: 45, width: 50, height: 20 },
          groupStyle: { left: 0, top: 0, width: 0, height: 0 }
        }
      ]
    }

    createGroupStyle(group)

    expect(group.propValue[0].groupStyle).toEqual({
      left: 0.25,
      top: 0.25,
      width: 0.25,
      height: 0.2
    })
    expect(group.propValue[0].style.left).toBe(50)
    expect(group.propValue[0].style.top).toBe(25)

    groupStyleRevert(group.propValue[0], { width: 100, height: 50 })
    expect(group.propValue[0].groupStyle).toEqual({ left: 0.5, top: 0.5, width: 0.5, height: 0.4 })
  })

  it('adapts child positions from group ratios and tab insertion defaults', () => {
    const component = {
      style: { left: 0, top: 0, width: 0, height: 0 },
      groupStyle: { left: 0.1, top: 0.2, width: 0.3, height: 0.4 }
    }

    groupItemStyleAdaptor(component, { width: 200, height: 100 })
    expect(component.style).toEqual({ left: 20, top: 20, width: 60, height: 40 })

    const innerComponent = {
      style: { left: 10, top: 12, width: 40, height: 20 },
      groupStyle: { left: 0, top: 0, width: 0, height: 0 }
    }
    dataVTabComponentAdd(innerComponent, { style: { width: 300, height: 200 }, showTabTitle: true })
    expect(innerComponent.style.left).toBe(0)
    expect(innerComponent.style.top).toBe(0)
    expect(innerComponent.groupStyle).toEqual({
      left: 0,
      top: 0,
      width: 40 / 300,
      height: 20 / 154
    })
  })
})
