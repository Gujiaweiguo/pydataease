import { describe, it, expect, vi, beforeEach } from 'vitest'
import { vClickOutside } from '../ClickOutside'

describe('vClickOutside', () => {
  let addSpy: ReturnType<typeof vi.spyOn>
  let removeSpy: ReturnType<typeof vi.spyOn>

  beforeEach(() => {
    addSpy = vi.spyOn(document, 'addEventListener')
    removeSpy = vi.spyOn(document, 'removeEventListener')
  })

  it('should add click listener to document on beforeMount', () => {
    const el = { contains: vi.fn(() => false) }
    const callback = vi.fn()

    vClickOutside.beforeMount(el, { value: callback })

    expect(addSpy).toHaveBeenCalledWith('click', expect.any(Function))
    expect((el as any).clickOutsideEvent).toBeDefined()
  })

  it('should trigger callback when clicking outside the element', () => {
    const callback = vi.fn()
    const el = { contains: vi.fn(() => false) }

    vClickOutside.beforeMount(el, { value: callback })

    const outsideTarget = document.createElement('div')
    const event = { target: outsideTarget } as unknown as Event
    ;(el as any).clickOutsideEvent(event)

    expect(callback).toHaveBeenCalledWith(event)
  })

  it('should NOT trigger callback when clicking inside the element', () => {
    const callback = vi.fn()
    const el = { contains: vi.fn(() => true) }

    vClickOutside.beforeMount(el, { value: callback })

    const innerTarget = document.createElement('span')
    const event = { target: innerTarget } as unknown as Event
    ;(el as any).clickOutsideEvent(event)

    expect(callback).not.toHaveBeenCalled()
  })

  it('should NOT trigger callback when event target is the element itself', () => {
    const callback = vi.fn()
    const el = { contains: vi.fn(() => false) }

    vClickOutside.beforeMount(el, { value: callback })

    const event = { target: el } as unknown as Event
    ;(el as any).clickOutsideEvent(event)

    expect(callback).not.toHaveBeenCalled()
  })

  it('should remove click listener from document on unmounted', () => {
    const el = { contains: vi.fn(() => false), clickOutsideEvent: vi.fn() }

    vClickOutside.unmounted(el)

    expect(removeSpy).toHaveBeenCalledWith('click', (el as any).clickOutsideEvent)
  })

  it('should not call callback if binding value is not a function', () => {
    const el = { contains: vi.fn(() => false) }

    vClickOutside.beforeMount(el, { value: 'not-a-function' })

    const outsideTarget = document.createElement('div')
    const event = { target: outsideTarget } as unknown as Event
    // Should not throw even though binding.value is not a function
    expect(() => (el as any).clickOutsideEvent(event)).not.toThrow()
  })
})
