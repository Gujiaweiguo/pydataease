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

import VTextComponent from '../Component.vue'

const createElement = () => ({
  id: 'text-1',
  propValue: 'Hello World',
  style: { verticalAlign: 'middle' },
  isLock: false
})

const mountComponent = (editMode = 'preview') => {
  vi.doMock('@/store/modules/data-visualization/dvMain', () => ({
    dvMainStoreWithOut: () => ({
      editMode,
      curComponent: createElement()
    })
  }))

  return shallowMount(VTextComponent, {
    props: {
      propValue: 'Hello World',
      element: createElement()
    },
    global: {
      mocks: { $t: (key: string) => key }
    }
  })
}

describe('v-text/Component', () => {
  it('renders in preview mode', () => {
    const wrapper = mountComponent('preview')
    expect(wrapper.find('.v-text').exists()).toBe(true)
    expect(wrapper.find('.preview').exists()).toBe(true)
  })

  it('renders in edit mode', () => {
    const wrapper = mountComponent('edit')
    expect(wrapper.find('.v-text').exists()).toBe(true)
  })

  it('accepts propValue prop', () => {
    const wrapper = mountComponent()
    expect(wrapper.props('propValue')).toBe('Hello World')
  })

  it('accepts element prop', () => {
    const wrapper = mountComponent()
    expect(wrapper.props('element').id).toBe('text-1')
  })

  it('emits input event', async () => {
    const wrapper = mountComponent('edit')
    const vm = wrapper.vm as any
    vm.handleInput({ target: { innerHTML: 'New text' } })
    expect(wrapper.emitted('input')).toBeTruthy()
  })
})
