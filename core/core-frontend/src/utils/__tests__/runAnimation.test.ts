import { describe, expect, it, vi } from 'vitest'

import runAnimation from '../runAnimation'

type ListenerMap = Record<string, Array<() => void>>

const createAnimationElement = () => {
  const listeners: ListenerMap = {}
  const addedClasses: string[] = []
  const removedClasses: string[] = []
  const setProperty = vi.fn()
  const removeProperty = vi.fn()

  const element = {
    classList: {
      add: vi.fn((...tokens: string[]) => {
        addedClasses.push(...tokens)
      }),
      remove: vi.fn((...tokens: string[]) => {
        removedClasses.push(...tokens)
      })
    },
    style: {
      setProperty,
      removeProperty
    },
    addEventListener: vi.fn((eventName: string, callback: () => void) => {
      listeners[eventName] ||= []
      listeners[eventName].push(callback)
    }),
    removeEventListener: vi.fn((eventName: string, callback: () => void) => {
      listeners[eventName] = (listeners[eventName] || []).filter(listener => listener !== callback)
    })
  }

  return {
    element,
    addedClasses,
    removedClasses,
    listeners,
    dispatch(eventName: string) {
      const callbacks = [...(listeners[eventName] || [])]
      callbacks.forEach(callback => {
        callback()
      })
    }
  }
}

describe('runAnimation', () => {
  it('resolves immediately when there are no animations', async () => {
    const { element } = createAnimationElement()

    await expect(runAnimation(element)).resolves.toBeUndefined()
    expect(element.classList.add).not.toHaveBeenCalled()
  })

  it('plays one animation and removes transient classes on animation end', async () => {
    const animationElement = createAnimationElement()
    const promise = runAnimation(animationElement.element, [
      { animationTime: 1.2, value: 'fadeInUp', isLoop: false }
    ])

    expect(animationElement.element.style.setProperty).toHaveBeenCalledWith('--time', '1.2s')
    expect(animationElement.addedClasses).toEqual(['fadeInUp', 'animated', 'no-infinite'])

    animationElement.dispatch('animationend')
    await promise

    expect(animationElement.removedClasses).toEqual(['fadeInUp', 'animated', 'no-infinite'])
    expect(animationElement.element.style.removeProperty).toHaveBeenCalledWith('--time')
  })

  it('uses the infinite class for looping animations', async () => {
    const animationElement = createAnimationElement()
    const promise = runAnimation(animationElement.element, [
      { animationTime: 0.8, value: 'pulse', isLoop: true }
    ])

    expect(animationElement.addedClasses).toContain('infinite')

    animationElement.dispatch('animationend')
    await promise

    expect(animationElement.removedClasses).toContain('infinite')
  })

  it('waits for each animation before starting the next one', async () => {
    const animationElement = createAnimationElement()
    const promise = runAnimation(animationElement.element, [
      { animationTime: 1, value: 'fadeIn', isLoop: false },
      { animationTime: 2, value: 'bounceIn', isLoop: false }
    ])

    expect(animationElement.element.classList.add).toHaveBeenCalledTimes(1)
    animationElement.dispatch('animationend')
    await Promise.resolve()

    expect(animationElement.element.classList.add).toHaveBeenCalledTimes(2)
    expect(animationElement.addedClasses).toEqual([
      'fadeIn',
      'animated',
      'no-infinite',
      'bounceIn',
      'animated',
      'no-infinite'
    ])

    animationElement.dispatch('animationend')
    await promise
  })

  it('also resolves when an animation is cancelled', async () => {
    const animationElement = createAnimationElement()
    const promise = runAnimation(animationElement.element, [
      { animationTime: 0.5, value: 'zoomIn', isLoop: false }
    ])

    animationElement.dispatch('animationcancel')
    await promise

    expect(animationElement.removedClasses).toEqual(['zoomIn', 'animated', 'no-infinite'])
    expect(animationElement.listeners.animationend).toHaveLength(0)
    expect(animationElement.listeners.animationcancel).toHaveLength(0)
  })
})
