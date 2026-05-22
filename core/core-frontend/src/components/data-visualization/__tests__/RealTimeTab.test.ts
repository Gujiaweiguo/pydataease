import { defineComponent } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  areaDataRef,
  curTabNameRef,
  eventBusEmitMock,
  recordSnapshotCacheMock,
  setCurTabNameMock,
  syncViewTitleMock
} = vi.hoisted(() => {
  const areaDataRef = { value: { components: [] as Array<Record<string, unknown>> } }
  const curTabNameRef = { value: '' as string | null }

  return {
    areaDataRef,
    curTabNameRef,
    eventBusEmitMock: vi.fn(),
    recordSnapshotCacheMock: vi.fn(),
    setCurTabNameMock: vi.fn((name: string | null) => {
      curTabNameRef.value = name
    }),
    syncViewTitleMock: vi.fn()
  }
})

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => `t:${key}` })
}))

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: vi.fn(() => ({})),
  storeToRefs: (store: Record<string, unknown>) => store
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    curTabName: curTabNameRef,
    setCurTabName: setCurTabNameMock
  })
}))

vi.mock('@/store/modules/data-visualization/compose', () => ({
  composeStoreWithOut: () => ({
    areaData: areaDataRef
  })
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: recordSnapshotCacheMock
  })
}))

vi.mock('@/utils/eventBus', () => ({
  default: {
    emit: eventBusEmitMock
  }
}))

vi.mock('@/utils/canvasUtils', () => ({
  syncViewTitle: syncViewTitleMock
}))

vi.mock('@/components/data-visualization/RealTimeGroup.vue', () => ({
  default: defineComponent({
    name: 'RealTimeGroup',
    props: {
      componentData: {
        type: Array,
        default: () => []
      }
    },
    template: '<div class="real-time-group-stub">{{ componentData.length }}</div>'
  })
}))

vi.mock('@/assets/svg/tab-title.svg', () => ({
  default: { name: 'TabTitleSvg', template: '<svg class="tab-title-svg" />' }
}))

vi.mock('@/assets/svg/dv-expand-down.svg', () => ({
  default: { name: 'DvExpandDownSvg', template: '<svg class="expand-down-svg" />' }
}))

vi.mock('@/assets/svg/dv-expand-right.svg', () => ({
  default: { name: 'DvExpandRightSvg', template: '<svg class="expand-right-svg" />' }
}))

import RealTimeTab from '../RealTimeTab.vue'

const DraggableStub = defineComponent({
  name: 'draggable',
  props: {
    list: {
      type: Array,
      default: () => []
    }
  },
  emits: ['end'],
  template: `
    <div class="draggable-stub">
      <slot name="item" v-for="(_, index) in list" :index="index" :key="index" />
    </div>
  `
})

const ElRowStub = defineComponent({
  name: 'ElRow',
  template: '<div class="el-row-stub"><slot /></div>'
})

const ElIconStub = defineComponent({
  name: 'ElIcon',
  emits: ['click'],
  template:
    '<button class="el-icon-stub" type="button" @click="$emit(\'click\', $event)"><slot /></button>'
})

const IconStub = defineComponent({
  name: 'Icon',
  template: '<span class="icon-stub"><slot /></span>'
})

const mountComponent = (componentData?: Array<Record<string, any>>) =>
  shallowMount(RealTimeTab, {
    props: {
      tabElement: { id: 'tab_1' },
      componentData: componentData ?? [
        { componentData: [], expand: false, id: '1', name: 'tab_1', title: 'Overview' },
        { componentData: [], expand: true, id: '2', name: 'tab_2', title: 'Detail' }
      ]
    },
    global: {
      stubs: {
        draggable: DraggableStub,
        ElIcon: ElIconStub,
        ElRow: ElRowStub,
        Icon: IconStub,
        Teleport: true
      }
    }
  })

describe('RealTimeTab', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    ;(HTMLInputElement.prototype.focus as () => void) = vi.fn()
    areaDataRef.value.components = [{ id: 'selected' }]
    curTabNameRef.value = ''
  })

  it('selects a tab and clears the compose selection area', async () => {
    const wrapper = mountComponent()

    await wrapper.findAll('.component-item')[0].trigger('click')

    expect(setCurTabNameMock).toHaveBeenCalledWith('tab_1')
    expect(areaDataRef.value.components).toEqual([])
  })

  it('toggles group expansion and renders the nested group component', async () => {
    const componentData = [
      { componentData: [{ id: 'child' }], expand: false, id: '1', name: 'tab_1', title: 'Overview' }
    ]
    const wrapper = mountComponent(componentData)

    expect(wrapper.findComponent({ name: 'RealTimeGroup' }).exists()).toBe(false)

    await wrapper.find('.component-expand').trigger('click')

    expect(componentData[0].expand).toBe(true)
    expect(wrapper.findComponent({ name: 'RealTimeGroup' }).exists()).toBe(true)
  })

  it('updates the current tab and records a snapshot after drag sorting', async () => {
    const wrapper = mountComponent()

    wrapper.findComponent(DraggableStub).vm.$emit('end', { newIndex: 1 })

    expect(setCurTabNameMock).toHaveBeenCalledWith('Detail')
    expect(eventBusEmitMock).toHaveBeenCalledWith('onTabSortChange-tab_1')
    expect(recordSnapshotCacheMock).toHaveBeenCalledWith('dragOnEnd')
  })

  it('renames a tab on blur and syncs the new title', async () => {
    const componentData = [
      { componentData: [], expand: false, id: '1', name: 'tab_1', title: 'Overview' }
    ]
    const wrapper = mountComponent(componentData)

    await wrapper.find('.component-label').trigger('dblclick')
    const input = wrapper.get('.custom-teleport')
    await input.setValue('Renamed View')
    await input.trigger('blur')

    expect(componentData[0].title).toBe('Renamed View')
    expect(syncViewTitleMock).toHaveBeenCalledWith(componentData[0])
  })
})
