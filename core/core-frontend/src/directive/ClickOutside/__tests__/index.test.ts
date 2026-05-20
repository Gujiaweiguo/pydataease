import { describe, it, expect, vi, beforeEach } from 'vitest'
import { vClickOutside } from '../index'

describe('vClickOutside', () => {
  let addSpy: ReturnType<typeof vi.spyOn>
  let removeSpy: ReturnType<typeof vi.spyOn>

  beforeEach(() => {
    addSpy = vi.spyOn(document, 'addEventListener')
    removeSpy = vi.spyOn(document, 'removeEventListener')
  })

  it('should add click listener on beforeMount', () => {
    const el = { contains: vi.fn(() => false) } as any
    const callback = vi.fn()

    vClickOutside.beforeMount(el, { value: callback } as any)

    expect(addSpy).toHaveBeenCalledWith('click', expect.any(Function))
    expect(el.clickOutsideEvent).toBeDefined()
  })

  it('should trigger callback when clicking outside', () => {
    const callback = vi.fn()
    const el = { contains: vi.fn(() => false) } as any

    vClickOutside.beforeMount(el, { value: callback } as any)

    const outsideTarget = document.createElement('div')
    const event = { target: outsideTarget } as unknown as Event
    el.clickOutsideEvent(event)

    expect(callback).toHaveBeenCalledWith(event)
  })

  it('should NOT trigger callback when clicking inside', () => {
    const callback = vi.fn()
    const el = { contains: vi.fn(() => true) } as any

    vClickOutside.beforeMount(el, { value: callback } as any)

    const innerTarget = document.createElement('span')
    const event = { target: innerTarget } as unknown as Event
    el.clickOutsideEvent(event)

    expect(callback).not.toHaveBeenCalled()
  })

  it('should NOT trigger callback when target is the element itself', () => {
    const callback = vi.fn()
    const el = { contains: vi.fn(() => false) } as any

    vClickOutside.beforeMount(el, { value: callback } as any)

    const event = { target: el } as unknown as Event
    el.clickOutsideEvent(event)

    expect(callback).not.toHaveBeenCalled()
  })

  it('should remove listener on unmounted', () => {
    const el = { contains: vi.fn(() => false) } as any
    vClickOutside.beforeMount(el, { value: vi.fn() } as any)

    vClickOutside.unmounted(el)

    expect(removeSpy).toHaveBeenCalledWith('click', el.clickOutsideEvent)
  })

  it('should not trigger if binding value is not a function', () => {
    const el = { contains: vi.fn(() => false) } as any
    vClickOutside.beforeMount(el, { value: 'not-a-func' } as any)

    const event = { target: document.createElement('div') } as unknown as Event
    expect(() => el.clickOutsideEvent(event)).not.toThrow()
  })
})
