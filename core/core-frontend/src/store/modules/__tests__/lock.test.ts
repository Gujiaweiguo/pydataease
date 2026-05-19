import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const { curComponent } = vi.hoisted(() => ({
  curComponent: {
    value: {
      component: 'Rect',
      isLock: false,
      propValue: [] as any[]
    }
  }
}))

vi.mock('pinia', async () => {
  const actual = await vi.importActual<typeof import('pinia')>('pinia')
  return {
    ...actual,
    storeToRefs: (store: any) => ({
      curComponent: store.curComponent
    })
  }
})

vi.mock('../data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    curComponent
  })
}))

import { lockStore } from '../data-visualization/lock'

describe('lockStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    curComponent.value = {
      component: 'Rect',
      isLock: false,
      propValue: []
    }
  })

  it('locks the current component by default', () => {
    const store = lockStore()

    store.lock()

    expect(curComponent.value.isLock).toBe(true)
  })

  it('unlocks the current component by default', () => {
    const store = lockStore()
    curComponent.value.isLock = true

    store.unlock()

    expect(curComponent.value.isLock).toBe(false)
  })

  it('locks all children when the target is a group', () => {
    const store = lockStore()
    const group = {
      component: 'Group',
      isLock: false,
      propValue: [{ isLock: false }, { isLock: false }]
    }

    store.lock(group as any)

    expect(group.isLock).toBe(true)
    expect(group.propValue.every(component => component.isLock)).toBe(true)
  })

  it('unlocks all children when the target is a group', () => {
    const store = lockStore()
    const group = {
      component: 'Group',
      isLock: true,
      propValue: [{ isLock: true }, { isLock: true }]
    }

    store.unlock(group as any)

    expect(group.isLock).toBe(false)
    expect(group.propValue.every(component => component.isLock === false)).toBe(true)
  })

  it('only updates the provided component when it is not a group', () => {
    const store = lockStore()
    const target = {
      component: 'Table',
      isLock: false,
      propValue: [{ isLock: false }]
    }

    store.lock(target as any)

    expect(target.isLock).toBe(true)
    expect(target.propValue[0].isLock).toBe(false)
  })
})
