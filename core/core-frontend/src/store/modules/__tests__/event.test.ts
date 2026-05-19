import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createTestingPinia } from '@pinia/testing'
import { setActivePinia } from 'pinia'

const { curComponent, componentData, canvasStateChange } = vi.hoisted(() => ({
  curComponent: { value: { events: {} as Record<string, any> } },
  componentData: { value: [] as any[] },
  canvasStateChange: vi.fn()
}))

vi.mock('pinia', async () => {
  const actual = await vi.importActual<typeof import('pinia')>('pinia')
  return {
    ...actual,
    storeToRefs: (store: any) => ({
      curComponent: store.curComponent,
      componentData: store.componentData
    })
  }
})

vi.mock('../data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    curComponent,
    componentData,
    canvasStateChange
  })
}))

import { eventStore } from '../data-visualization/event'

describe('eventStore', () => {
  beforeEach(() => {
    setActivePinia(createTestingPinia({ createSpy: vi.fn, stubActions: false }))
    curComponent.value = {
      events: {
        displayChange: { value: false }
      }
    }
    componentData.value = []
    canvasStateChange.mockReset()
    vi.stubGlobal('area', 'hidden')
  })

  it('adds events to the current component', () => {
    const store = eventStore()

    store.addEvent({ event: 'redirect', param: '/dashboard' })

    expect(curComponent.value.events.redirect).toBe('/dashboard')
  })

  it('overwrites an existing event when adding the same key again', () => {
    const store = eventStore()

    store.addEvent({ event: 'redirect', param: '/first' })
    store.addEvent({ event: 'redirect', param: '/second' })

    expect(curComponent.value.events.redirect).toBe('/second')
  })

  it('removes existing events from the current component', () => {
    const store = eventStore()
    curComponent.value.events.alert = 'hello'

    store.removeEvent('alert')

    expect(curComponent.value.events.alert).toBeUndefined()
  })

  it('ignores removing event keys that do not exist', () => {
    const store = eventStore()

    expect(() => store.removeEvent('missing')).not.toThrow()
    expect(curComponent.value.events).toEqual({ displayChange: { value: false } })
  })

  it('toggles displayChange visibility state', () => {
    const store = eventStore()
    const component = {
      events: {
        displayChange: { value: false }
      }
    }

    store.displayEventChange(component as any)

    expect(component.events.displayChange.value).toBe(true)
    expect(canvasStateChange).toHaveBeenCalledWith({ key: 'curPointArea', value: 'hidden' })
  })

  it('updates hidden components to match the display change value', () => {
    const store = eventStore()
    const component = {
      events: {
        displayChange: { value: true }
      }
    }
    componentData.value = [
      { id: 1, category: 'hidden', isShow: false },
      { id: 2, category: 'base', isShow: false },
      { id: 3, category: 'hidden', isShow: false }
    ]

    store.displayEventChange(component as any)

    expect(component.events.displayChange.value).toBe(false)
    expect(componentData.value[0].isShow).toBe(false)
    expect(componentData.value[1].isShow).toBe(false)
    expect(componentData.value[2].isShow).toBe(false)
  })
})
