import { describe, expect, it } from 'vitest'

import decomposeComponent from '../decomposeComponent'

type TestComponent = {
  canvasId?: string
  style: {
    left: number
    top: number
  }
  groupStyle?: {
    left: number
    top: number
    width: number
    height: number
  }
}

describe('decomposeComponent', () => {
  it('offsets component coordinates and uses the default canvas id', () => {
    const component: TestComponent = {
      style: { left: 10, top: 15 }
    }

    decomposeComponent(component, null, { left: 5, top: 7 })

    expect(component.style).toMatchObject({ left: 15, top: 22 })
    expect(component.canvasId).toBe('canvas-main')
  })

  it('applies a custom canvas id when provided', () => {
    const component: TestComponent = {
      style: { left: 0, top: 0 }
    }

    decomposeComponent(component, null, { left: 12, top: 8 }, 'canvas-tab-1')

    expect(component.canvasId).toBe('canvas-tab-1')
    expect(component.style).toMatchObject({ left: 12, top: 8 })
  })

  it('rescales nested group styles relative to the parent group', () => {
    const component: TestComponent = {
      style: { left: 4, top: 6 },
      groupStyle: { left: 20, top: 10, width: 40, height: 20 }
    }

    decomposeComponent(component, null, { left: 100, top: 50 }, 'canvas-main', {
      width: 2,
      height: 3
    })

    expect(component.style).toMatchObject({ left: 104, top: 56 })
    expect(component.groupStyle).toEqual({ left: 140, top: 80, width: 80, height: 60 })
  })

  it('leaves groupStyle unchanged when parent group scaling is missing', () => {
    const component: TestComponent = {
      style: { left: 1, top: 2 },
      groupStyle: { left: 5, top: 6, width: 10, height: 20 }
    }

    decomposeComponent(component, null, { left: 3, top: 4 })

    expect(component.groupStyle).toEqual({ left: 5, top: 6, width: 10, height: 20 })
  })

  it('handles components without groupStyle even when parent scaling exists', () => {
    const component: TestComponent = {
      style: { left: -10, top: 20 }
    }

    decomposeComponent(component, null, { left: 8, top: -5 }, 'canvas-group-1', {
      width: 4,
      height: 4
    })

    expect(component.style).toMatchObject({ left: -2, top: 15 })
    expect(component.canvasId).toBe('canvas-group-1')
  })
})
