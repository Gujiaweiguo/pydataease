import { beforeEach, describe, expect, it, vi } from 'vitest'

const { onBeforeUnmountMock } = vi.hoisted(() => ({
  onBeforeUnmountMock: vi.fn()
}))

vi.mock('vue', async () => {
  const actual = await vi.importActual<typeof import('vue')>('vue')
  return {
    ...actual,
    onBeforeUnmount: onBeforeUnmountMock
  }
})

import { useEmitt } from '../useEmitt'

describe('useEmitt', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    const { emitter } = useEmitt()
    ;(emitter as any).all.clear()
  })

  it('returns an emitter instance with mitt methods', () => {
    const { emitter } = useEmitt()

    expect(emitter).toBeDefined()
    expect(typeof emitter.on).toBe('function')
    expect(typeof emitter.off).toBe('function')
    expect(typeof emitter.emit).toBe('function')
  })

  it('reuses the same emitter across invocations', () => {
    const first = useEmitt().emitter
    const second = useEmitt().emitter

    expect(first).toBe(second)
  })

  it('registers the provided callback immediately', () => {
    const callback = vi.fn()
    const { emitter } = useEmitt({ name: 'refresh', callback })

    emitter.emit('refresh', 'payload')

    expect(callback).toHaveBeenCalledTimes(1)
    expect(callback).toHaveBeenCalledWith('payload')
  })

  it('registers cleanup with onBeforeUnmount when an option is provided', () => {
    const callback = vi.fn()

    useEmitt({ name: 'refresh', callback })

    expect(onBeforeUnmountMock).toHaveBeenCalledTimes(1)
    expect(typeof onBeforeUnmountMock.mock.calls[0][0]).toBe('function')
  })

  it('removes the registered listener during cleanup', () => {
    const callback = vi.fn()
    const { emitter } = useEmitt({ name: 'refresh', callback })
    const cleanup = onBeforeUnmountMock.mock.calls[0][0] as () => void

    cleanup()
    emitter.emit('refresh', 'payload')

    expect(callback).not.toHaveBeenCalled()
  })

  it('does not register lifecycle cleanup without an option', () => {
    useEmitt()

    expect(onBeforeUnmountMock).not.toHaveBeenCalled()
  })
})
