import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/utils/DeShortcutKey.js', () => ({
  keycodes: [65, 67, 86, 88]
}))

vi.mock('@/utils/eventBus', () => ({
  default: { on: vi.fn(), off: vi.fn(), emit: vi.fn() }
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    editMode: 'preview',
    curComponent: { id: 'test-id', propValue: '' }
  })
}))

vi.mock('pinia', () => ({
  storeToRefs: (store: any) => ({
    editMode: { value: store.editMode },
    curComponent: { value: store.curComponent }
  }),
  defineStore: vi.fn()
}))

import ScrollTextComponent from '../Component.vue'

const createElement = () => ({
  id: 'scroll-1',
  propValue: 'Scrolling Text',
  style: { verticalAlign: 'middle', scrollSpeed: 10 },
  isLock: false,
  resizing: false,
  dragging: false
})

const mountComponent = (editMode = 'preview') =>
  shallowMount(ScrollTextComponent, {
    props: {
      propValue: 'Scrolling Text',
      element: createElement(),
      showPosition: 'preview'
    },
    global: {
      mocks: { $t: (key: string) => key }
    }
  })

describe('scroll-text/Component', () => {
  it('renders in preview mode', () => {
    const wrapper = mountComponent('preview')
    expect(wrapper.find('.v-text').exists()).toBe(true)
    expect(wrapper.find('.preview').exists()).toBe(true)
  })

  it('renders in edit mode', () => {
    const wrapper = shallowMount(ScrollTextComponent, {
      props: {
        propValue: 'Scrolling Text',
        element: createElement(),
        showPosition: 'canvas'
      },
      global: { mocks: { $t: (key: string) => key } }
    })
    expect(wrapper.find('.v-text').exists()).toBe(true)
  })

  it('accepts propValue prop', () => {
    const wrapper = mountComponent()
    expect(wrapper.props('propValue')).toBe('Scrolling Text')
  })

  it('accepts element prop', () => {
    const wrapper = mountComponent()
    expect(wrapper.props('element').id).toBe('scroll-1')
  })

  it('accepts showPosition prop', () => {
    const wrapper = mountComponent()
    expect(wrapper.props('showPosition')).toBe('preview')
  })
})
