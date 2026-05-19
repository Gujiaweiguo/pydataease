import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const { curComponent } = vi.hoisted(() => ({
  curComponent: {
    value: {
      animations: [] as Array<Record<string, any>>
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

import { animationStore } from '../data-visualization/animation'

describe('animationStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    curComponent.value = {
      animations: [
        { type: 'fadeIn', duration: 1, delay: 0 },
        { type: 'slideIn', duration: 2, delay: 0.5 }
      ]
    }
  })

  it('adds an animation to the current component', () => {
    const store = animationStore()

    store.addAnimation({ type: 'bounce', duration: 3 })

    expect(curComponent.value.animations).toHaveLength(3)
    expect(curComponent.value.animations[2]).toEqual({ type: 'bounce', duration: 3 })
  })

  it('removes an animation by index', () => {
    const store = animationStore()

    store.removeAnimation(0)

    expect(curComponent.value.animations).toEqual([{ type: 'slideIn', duration: 2, delay: 0.5 }])
  })

  it('leaves animations unchanged when removing an out-of-range index', () => {
    const store = animationStore()

    store.removeAnimation(99)

    expect(curComponent.value.animations).toHaveLength(2)
  })

  it('merges updated fields into an existing animation', () => {
    const store = animationStore()

    store.alterAnimation({ index: 1, data: { duration: 5, timing: 'ease-in' } })

    expect(curComponent.value.animations[1]).toEqual({
      type: 'slideIn',
      duration: 5,
      delay: 0.5,
      timing: 'ease-in'
    })
  })

  it('ignores alterAnimation calls when index is not a number', () => {
    const store = animationStore()

    store.alterAnimation({ index: '1', data: { duration: 9 } })

    expect(curComponent.value.animations[1]).toEqual({ type: 'slideIn', duration: 2, delay: 0.5 })
  })
})
