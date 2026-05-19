import { beforeEach, describe, expect, it, vi } from 'vitest'

import { useScrollTo } from '../useScrollTo'

describe('useScrollTo', () => {
  let frameQueue: FrameRequestCallback[]

  const flushFrames = () => {
    while (frameQueue.length > 0) {
      const callback = frameQueue.shift()
      callback?.(performance.now())
    }
  }

  beforeEach(() => {
    frameQueue = []
    vi.stubGlobal(
      'requestAnimationFrame',
      vi.fn((callback: FrameRequestCallback) => {
        frameQueue.push(callback)
        return frameQueue.length
      })
    )
  })

  it('animates scrollLeft to the target value and calls the callback once', () => {
    const callback = vi.fn()
    const el = { scrollLeft: 0 } as HTMLElement
    const controller = useScrollTo({ el, to: 100, position: 'scrollLeft', duration: 40, callback })

    controller.start()
    flushFrames()

    expect(el.scrollLeft).toBe(100)
    expect(callback).toHaveBeenCalledTimes(1)
  })

  it('supports animating custom positions such as scrollTop', () => {
    const el = { scrollTop: 10 } as HTMLElement
    const controller = useScrollTo({ el, to: 70, position: 'scrollTop', duration: 40 })

    controller.start()
    flushFrames()

    expect(el.scrollTop).toBe(70)
  })

  it('stops queued animation frames before the target is reached', () => {
    const callback = vi.fn()
    const el = { scrollLeft: 0 } as HTMLElement
    const controller = useScrollTo({ el, to: 120, position: 'scrollLeft', duration: 40, callback })

    controller.start()
    controller.stop()
    flushFrames()

    expect(el.scrollLeft).toBeGreaterThan(0)
    expect(el.scrollLeft).toBeLessThan(120)
    expect(callback).not.toHaveBeenCalled()
  })

  it('still invokes the callback when the start and target positions are the same', () => {
    const callback = vi.fn()
    const el = { scrollLeft: 48 } as HTMLElement
    const controller = useScrollTo({ el, to: 48, position: 'scrollLeft', duration: 40, callback })

    controller.start()
    flushFrames()

    expect(el.scrollLeft).toBe(48)
    expect(callback).toHaveBeenCalledTimes(1)
  })
})
