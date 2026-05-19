import { beforeEach, describe, expect, it, vi } from 'vitest'

import { useWatermark } from '../useWatermark'

describe('useWatermark', () => {
  const getOverlayCount = (container: ParentNode = document) =>
    container.querySelectorAll('[id="Symbol(watermark-dom)"]').length

  beforeEach(() => {
    vi.clearAllMocks()
    document.body.innerHTML = ''
    Object.defineProperty(document.documentElement, 'clientWidth', {
      value: 1280,
      configurable: true
    })
    Object.defineProperty(document.documentElement, 'clientHeight', {
      value: 720,
      configurable: true
    })
    vi.spyOn(HTMLCanvasElement.prototype, 'getContext').mockReturnValue({
      rotate: vi.fn(),
      fillText: vi.fn(),
      font: '',
      fillStyle: '',
      textAlign: '',
      textBaseline: ''
    } as unknown as CanvasRenderingContext2D)
    vi.spyOn(HTMLCanvasElement.prototype, 'toDataURL').mockReturnValue(
      'data:image/png;base64,watermark'
    )
  })

  it('creates a watermark overlay on the document body', () => {
    const { setWatermark } = useWatermark()

    setWatermark('DataEase')

    const overlay = document.getElementById('Symbol(watermark-dom)') as HTMLDivElement
    expect(overlay).not.toBeNull()
    expect(overlay.style.width).toBe('1280px')
    expect(overlay.style.height).toBe('720px')
    expect(overlay.style.background).toContain('data:image/png;base64,watermark')
    expect(overlay.style.pointerEvents).toBe('none')
  })

  it('clears the watermark from a custom container and unregisters resize listeners', () => {
    const container = document.createElement('section')
    document.body.appendChild(container)
    const removeListenerSpy = vi.spyOn(window, 'removeEventListener')
    const { clear, setWatermark } = useWatermark(container)

    setWatermark('Private')
    clear()

    expect(container.querySelector('[id="Symbol(watermark-dom)"]')).toBeNull()
    expect(removeListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function))
  })

  it('replaces an existing watermark instead of stacking duplicates', () => {
    const addListenerSpy = vi.spyOn(window, 'addEventListener')
    const { setWatermark } = useWatermark()

    setWatermark('First')
    setWatermark('Second')

    expect(getOverlayCount()).toBe(1)
    expect(addListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function))
  })

  it('recreates the watermark overlay when the window resizes', () => {
    const { setWatermark } = useWatermark()

    setWatermark('Resize me')
    const firstOverlay = document.getElementById('Symbol(watermark-dom)')

    window.dispatchEvent(new Event('resize'))

    const nextOverlay = document.getElementById('Symbol(watermark-dom)')
    expect(nextOverlay).not.toBe(firstOverlay)
    expect(getOverlayCount()).toBe(1)
  })
})
