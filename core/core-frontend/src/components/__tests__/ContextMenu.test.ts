import { defineComponent, ref } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const storeState = vi.hoisted(() => ({
  menuTop: null as any,
  menuLeft: null as any,
  menuShow: null as any,
  position: null as any
}))

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: (store: Record<string, unknown>) => store
}))

vi.mock('@/store/modules/data-visualization/contextmenu', () => ({
  contextmenuStoreWithOut: () => storeState
}))

vi.mock('@/components/data-visualization/canvas/ContextMenuDetails.vue', () => ({
  default: defineComponent({
    name: 'ContextMenuDetails',
    template: '<div class="context-menu-details-stub"></div>'
  })
}))

import ContextMenu from '@/components/data-visualization/canvas/ContextMenu.vue'

describe('ContextMenu', () => {
  beforeEach(() => {
    // ref already imported at top
    storeState.menuTop = ref(20)
    storeState.menuLeft = ref(40)
    storeState.menuShow = ref(true)
    storeState.position = ref('canvasCore')
  })

  it('shows details when menu is visible for the current position', () => {
    const wrapper = mount(ContextMenu)

    expect(wrapper.find('.context-menu-details-stub').exists()).toBe(true)
    expect(wrapper.getComponent({ name: 'ContextMenuDetails' }).isVisible()).toBe(true)
  })

  it('passes top and left styles from the context menu store', () => {
    const wrapper = mount(ContextMenu)

    expect(wrapper.getComponent({ name: 'ContextMenuDetails' }).attributes('style')).toContain(
      'top: 20px;'
    )
    expect(wrapper.getComponent({ name: 'ContextMenuDetails' }).attributes('style')).toContain(
      'left: 40px;'
    )
  })

  it('hides details when the requested position differs', () => {
    storeState.position.value = 'aside'
    const wrapper = mount(ContextMenu)

    expect(wrapper.getComponent({ name: 'ContextMenuDetails' }).attributes('style')).toContain(
      'display: none;'
    )
  })
})
