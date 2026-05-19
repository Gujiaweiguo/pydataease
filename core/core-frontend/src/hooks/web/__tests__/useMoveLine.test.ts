import { beforeEach, describe, expect, it, vi } from 'vitest'

const { emitMock, mountedCallbacks, unmountedCallbacks, wsCacheMock } = vi.hoisted(() => ({
  emitMock: vi.fn(),
  mountedCallbacks: [] as Array<() => void>,
  unmountedCallbacks: [] as Array<() => void>,
  wsCacheMock: {
    get: vi.fn(),
    set: vi.fn()
  }
}))

vi.mock('vue', async () => {
  const actual = await vi.importActual<typeof import('vue')>('vue')
  return {
    ...actual,
    onMounted: (callback: () => void) => mountedCallbacks.push(callback),
    onBeforeUnmount: (callback: () => void) => unmountedCallbacks.push(callback)
  }
})

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({ wsCache: wsCacheMock })
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({ emitter: { emit: emitMock } })
}))

import { useMoveLine } from '../useMoveLine'

describe('useMoveLine', () => {
  beforeEach(() => {
    document.dispatchEvent(new MouseEvent('mouseup'))
    vi.clearAllMocks()
    mountedCallbacks.length = 0
    unmountedCallbacks.length = 0
    wsCacheMock.get.mockReturnValue(undefined)
    document.body.innerHTML = ''
    document.body.style.userSelect = ''
  })

  it('initializes width from cache or falls back to 280 and stores the collapse bar width', () => {
    wsCacheMock.get.mockReturnValueOnce(undefined)

    const { width } = useMoveLine('DATASET')

    expect(wsCacheMock.get).toHaveBeenCalledWith('DATASET')
    expect(width.value).toBe(280)
    expect(wsCacheMock.set).toHaveBeenCalledWith('current-collapse_bar', 280)
  })

  it('mounts a drag line and clamps width to the max bound while emitting updates', () => {
    wsCacheMock.get.mockReturnValueOnce(300)
    const container = document.createElement('div')
    document.body.appendChild(container)
    const { node, width } = useMoveLine('DASHBOARD')
    node.value = container

    mountedCallbacks[0]()

    const line = container.querySelector('.sidebar-move-line') as HTMLDivElement
    line.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }))
    document.dispatchEvent(new MouseEvent('mousemove', { clientX: 450 }))

    expect(line).not.toBeNull()
    expect(width.value).toBe(401)
    expect(line.style.left).toBe('396px')
    expect(wsCacheMock.set).toHaveBeenCalledWith('current-collapse_bar', 401)
    expect(emitMock).toHaveBeenCalledWith('current-collapse_bar')
  })

  it('restores drag state on mouseup and removes the mousemove listener', () => {
    const container = document.createElement('div')
    document.body.appendChild(container)
    const { node, width } = useMoveLine('DATASOURCE')
    node.value = container

    mountedCallbacks[0]()

    const line = container.querySelector('.sidebar-move-line') as HTMLDivElement
    line.dispatchEvent(new MouseEvent('mousedown', { bubbles: true }))
    document.dispatchEvent(new MouseEvent('mousemove', { clientX: 279 }))
    document.dispatchEvent(new MouseEvent('mouseup'))

    const savedWidth = width.value
    document.dispatchEvent(new MouseEvent('mousemove', { clientX: 330 }))

    expect(line.className).toBe('sidebar-move-line')
    expect(width.value).toBe(savedWidth)
    expect(wsCacheMock.set).toHaveBeenCalledWith('DATASOURCE', savedWidth)
  })

  it('removes the drag line on unmount for component refs and clears width', () => {
    const container = document.createElement('div')
    document.body.appendChild(container)
    const { node, width } = useMoveLine('DATA-FILLING')
    node.value = { $el: container }

    mountedCallbacks[0]()
    expect(container.querySelector('.sidebar-move-line')).not.toBeNull()

    unmountedCallbacks[0]()

    expect(container.querySelector('.sidebar-move-line')).toBeNull()
    expect(width.value).toBeNull()
  })
})
