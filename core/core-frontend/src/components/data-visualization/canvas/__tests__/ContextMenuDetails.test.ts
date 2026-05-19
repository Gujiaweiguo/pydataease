import { defineComponent } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const menuState = vi.hoisted(() => ({
  curComponent: null as any,
  componentData: null as any,
  areaData: null as any,
  dvMainActions: {
    setClickComponentStatus: vi.fn(),
    canvasStateChange: vi.fn(),
    deleteComponentById: vi.fn()
  },
  copyActions: {
    cut: vi.fn(),
    copy: vi.fn(),
    paste: vi.fn()
  },
  lockActions: {
    lock: vi.fn(),
    unlock: vi.fn()
  },
  snapshotActions: {
    recordSnapshotCache: vi.fn()
  },
  layerActions: {
    hideComponentWithComponent: vi.fn(),
    showComponent: vi.fn(),
    upComponent: vi.fn(),
    downComponent: vi.fn(),
    topComponent: vi.fn(),
    bottomComponent: vi.fn()
  },
  composeActions: {
    compose: vi.fn(),
    decompose: vi.fn(),
    alignment: vi.fn()
  },
  emitter: {
    emit: vi.fn()
  },
  eventBus: {
    emit: vi.fn()
  },
  common: {
    getCurInfo: vi.fn(() => ({ componentData: ['cur-info'] })),
    componentArraySort: vi.fn()
  }
}))

vi.mock('pinia', () => ({
  storeToRefs: (store: Record<string, unknown>) => store
}))

vi.mock('@/store/modules/data-visualization/dvMain', async () => {
  const { ref } = await import('vue')
  menuState.curComponent ||= ref(null)
  menuState.componentData ||= ref([])

  return {
    dvMainStoreWithOut: () => ({
      curComponent: menuState.curComponent,
      componentData: menuState.componentData,
      ...menuState.dvMainActions
    })
  }
})

vi.mock('@/store/modules/data-visualization/lock', () => ({
  lockStoreWithOut: () => menuState.lockActions
}))

vi.mock('@/store/modules/data-visualization/copy', () => ({
  copyStoreWithOut: () => menuState.copyActions
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => menuState.snapshotActions
}))

vi.mock('@/store/modules/data-visualization/layer', () => ({
  layerStoreWithOut: () => menuState.layerActions
}))

vi.mock('@/store/modules/data-visualization/compose', async () => {
  const { ref } = await import('vue')
  menuState.areaData ||= ref({ components: [] })

  return {
    composeStoreWithOut: () => ({
      areaData: menuState.areaData,
      ...menuState.composeActions
    })
  }
})

vi.mock('@/utils/eventBus', () => ({
  default: menuState.eventBus
}))

vi.mock('@/store/modules/data-visualization/common', () => ({
  componentArraySort: menuState.common.componentArraySort,
  getCurInfo: menuState.common.getCurInfo
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({ emitter: menuState.emitter })
}))

vi.mock('@/components/plugin', () => ({
  XpackComponent: defineComponent({
    name: 'XpackComponent',
    template: '<div class="xpack-component-stub"></div>'
  })
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => key
  })
}))

import ContextMenuDetails from '../ContextMenuDetails.vue'

const stubs = {
  ElDivider: defineComponent({
    name: 'ElDivider',
    template: '<div class="el-divider-stub"></div>'
  }),
  ElDropdown: defineComponent({
    name: 'ElDropdown',
    template: '<div class="el-dropdown-stub"><slot /><slot name="dropdown" /></div>'
  }),
  ElDropdownMenu: defineComponent({
    name: 'ElDropdownMenu',
    template: '<div class="el-dropdown-menu-stub"><slot /></div>'
  }),
  ElDropdownItem: defineComponent({
    name: 'ElDropdownItem',
    emits: ['click'],
    template: '<button class="el-dropdown-item-stub" @click="$emit(\'click\')"><slot /></button>'
  }),
  ElIcon: defineComponent({
    name: 'ElIcon',
    template: '<i class="el-icon-stub"><slot /></i>'
  }),
  ArrowRight: defineComponent({
    name: 'ArrowRight',
    template: '<span class="arrow-right-stub"></span>'
  })
}

const defaultComponent = () => ({
  id: 'component-1',
  component: 'VQuery',
  category: 'base',
  canvasId: 'canvas-main',
  isLock: false,
  isShow: true
})

const mountComponent = (props: Record<string, unknown> = {}) =>
  shallowMount(ContextMenuDetails, {
    props,
    global: {
      stubs
    }
  })

const findMenuItem = (wrapper: ReturnType<typeof mountComponent>, text: string) => {
  const item = wrapper.findAll('li').find(node => node.text().includes(text))

  if (!item) {
    throw new Error(`Menu item not found: ${text}`)
  }

  return item
}

describe('ContextMenuDetails', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    menuState.curComponent.value = null
    menuState.componentData.value = []
    menuState.areaData.value = { components: [] }
  })

  it('composes the selected area and emits close info in aside mode', async () => {
    menuState.areaData.value.components = [{ id: 'c-1' }, { id: 'c-2' }]
    const wrapper = mountComponent({ activePosition: 'aside' })

    await findMenuItem(wrapper, 'visualization.view_group').trigger('click')

    expect(menuState.composeActions.compose).toHaveBeenCalled()
    expect(menuState.snapshotActions.recordSnapshotCache).toHaveBeenCalledWith('componentCompose')
    expect(wrapper.emitted('close')).toContainEqual([{ opt: 'componentCompose' }])
  })

  it('locks the current component and records a snapshot', async () => {
    menuState.curComponent.value = defaultComponent()
    menuState.componentData.value = [menuState.curComponent.value]
    const wrapper = mountComponent({ activePosition: 'aside' })

    await findMenuItem(wrapper, 'visualization.lock').trigger('click')

    expect(menuState.lockActions.lock).toHaveBeenCalledWith()
    expect(menuState.snapshotActions.recordSnapshotCache).toHaveBeenCalledWith('lock')
    expect(wrapper.emitted('close')).toContainEqual([{ opt: 'lock' }])
  })

  it('moves a visible VQuery component into the hidden area', async () => {
    menuState.curComponent.value = defaultComponent()
    menuState.componentData.value = [menuState.curComponent.value]
    const wrapper = mountComponent()

    await findMenuItem(wrapper, 'visualization.move_to_pop_area').trigger('click')

    expect(menuState.curComponent.value?.category).toBe('hidden')
    expect(menuState.snapshotActions.recordSnapshotCache).toHaveBeenCalledWith('categoryChange')
    expect(menuState.dvMainActions.canvasStateChange).toHaveBeenCalledWith({
      key: 'curPointArea',
      value: 'hidden'
    })
  })

  it('deletes all selected area components and hides the area overlay', async () => {
    menuState.areaData.value.components = [{ id: 'a-1' }, { id: 'a-2' }]
    const wrapper = mountComponent({ activePosition: 'aside' })

    await findMenuItem(wrapper, 'visualization.delete').trigger('click')

    expect(menuState.dvMainActions.deleteComponentById).toHaveBeenNthCalledWith(1, 'a-1')
    expect(menuState.dvMainActions.deleteComponentById).toHaveBeenNthCalledWith(2, 'a-2')
    expect(menuState.eventBus.emit).toHaveBeenCalledWith('hideArea-canvas-main')
    expect(menuState.snapshotActions.recordSnapshotCache).toHaveBeenCalledWith('deleteComponent')
    expect(wrapper.emitted('close')).toContainEqual([{ opt: 'deleteComponent' }])
  })

  it('keeps the current selection active and closes on mouseup from aside', async () => {
    const wrapper = mountComponent({ activePosition: 'aside' })

    await wrapper.get('ul').trigger('mouseup')

    expect(menuState.dvMainActions.setClickComponentStatus).toHaveBeenCalledWith(true)
    expect(wrapper.emitted('close')).toHaveLength(1)
  })
})
