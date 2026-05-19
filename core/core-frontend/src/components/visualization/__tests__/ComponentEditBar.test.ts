import { defineComponent, nextTick, ref } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  batchOptStatus: null as any,
  pcMatrixCount: null as any,
  curComponent: null as any,
  componentData: null as any,
  canvasViewInfo: null as any,
  mobileInPc: null as any,
  dvInfo: null as any,
  isPopWindow: null as any,
  hiddenListStatus: null as any,
  recordSnapshotCache: vi.fn(),
  emitterEmit: vi.fn(),
  eventBusOn: vi.fn(),
  eventBusOff: vi.fn(),
  eventBusEmit: vi.fn(),
  addCurMultiplexingComponent: vi.fn(),
  removeCurMultiplexingComponentWithId: vi.fn(),
  addCurBatchComponent: vi.fn(),
  removeCurBatchComponentWithId: vi.fn(),
  isMobile: false,
  isMainCanvas: true
}))

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: (store: Record<string, unknown>) => store
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => key })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    batchOptStatus: mocks.batchOptStatus,
    pcMatrixCount: mocks.pcMatrixCount,
    curComponent: mocks.curComponent,
    componentData: mocks.componentData,
    canvasViewInfo: mocks.canvasViewInfo,
    mobileInPc: mocks.mobileInPc,
    dvInfo: mocks.dvInfo,
    isPopWindow: mocks.isPopWindow,
    hiddenListStatus: mocks.hiddenListStatus,
    addCurMultiplexingComponent: mocks.addCurMultiplexingComponent,
    removeCurMultiplexingComponentWithId: mocks.removeCurMultiplexingComponentWithId,
    addCurBatchComponent: mocks.addCurBatchComponent,
    removeCurBatchComponentWithId: mocks.removeCurBatchComponentWithId,
    setCurComponent: vi.fn(),
    setHiddenListStatus: vi.fn(),
    setLastHiddenComponent: vi.fn(),
    clearViewLinkage: vi.fn(),
    getViewInstanceInfo: vi.fn(),
    getViewDetails: vi.fn(),
    getViewDataDetails: vi.fn(),
    getLastViewRequestInfo: vi.fn()
  })
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: mocks.recordSnapshotCache })
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({ emitter: { emit: mocks.emitterEmit } })
}))

vi.mock('@/store/modules/data-visualization/copy', () => ({
  copyStoreWithOut: () => ({ copy: vi.fn(), paste: vi.fn() })
}))

vi.mock('@/views/chart/components/js/util', () => ({
  exportExcelDownload: vi.fn()
}))

vi.mock('@/views/chart/components/js/panel/common/common_table', () => ({
  exportPivotExcel: vi.fn()
}))

vi.mock('@/components/plugin', () => ({
  XpackComponent: defineComponent({ name: 'XpackComponent', template: '<div />' })
}))

vi.mock('@/utils/utils', () => ({
  exportPermission: () => [true, true],
  isMobile: () => mocks.isMobile
}))

vi.mock('@/utils/canvasUtils', () => ({
  isMainCanvas: () => mocks.isMainCanvas
}))

vi.mock('@/utils/eventBus', () => ({
  default: {
    on: mocks.eventBusOn,
    off: mocks.eventBusOff,
    emit: mocks.eventBusEmit
  }
}))

import ComponentEditBar from '../ComponentEditBar.vue'

const stubs = {
  ElTooltip: defineComponent({ name: 'ElTooltip', template: '<div><slot /></div>' }),
  ElIcon: defineComponent({
    name: 'ElIcon',
    emits: ['click'],
    template: '<button class="icon-stub" @click="$emit(\'click\', $event)"><slot /></button>'
  }),
  ElCheckbox: defineComponent({
    name: 'ElCheckbox',
    props: ['modelValue'],
    emits: ['update:modelValue', 'change'],
    template:
      '<input class="checkbox-stub" type="checkbox" :checked="modelValue" @change="$emit(\'update:modelValue\', $event.target.checked); $emit(\'change\', $event.target.checked)" />'
  }),
  ElDropdown: defineComponent({
    name: 'ElDropdown',
    methods: {
      handleClose() {
        /* noop */
      }
    },
    template: '<div class="dropdown-stub"><slot /><slot name="dropdown" /></div>'
  }),
  ElDropdownMenu: defineComponent({ name: 'ElDropdownMenu', template: '<div><slot /></div>' }),
  ElDropdownItem: defineComponent({
    name: 'ElDropdownItem',
    emits: ['click'],
    template: '<button class="dropdown-item-stub" @click="$emit(\'click\')"><slot /></button>'
  }),
  ElPopover: defineComponent({
    name: 'ElPopover',
    template: '<div class="popover-stub"><slot /><slot name="reference" /></div>'
  }),
  FieldsList: defineComponent({ name: 'FieldsList', template: '<div class="fields-list-stub" />' }),
  CustomTabsSort: defineComponent({
    name: 'CustomTabsSort',
    methods: {
      sortInit() {
        /* noop */
      }
    },
    template: '<div />'
  }),
  Icon: defineComponent({ name: 'Icon', template: '<span><slot /></span>' }),
  Sort: defineComponent({ name: 'Sort', template: '<svg />' }),
  ArrowRight: defineComponent({ name: 'ArrowRight', template: '<svg />' }),
  RefreshLeft: defineComponent({ name: 'RefreshLeft', template: '<svg />' }),
  icon_edit_outlined: defineComponent({ name: 'icon_edit_outlined', template: '<svg />' }),
  icon_add_outlined: defineComponent({ name: 'icon_add_outlined', template: '<svg />' }),
  dvBarEnlarge: defineComponent({ name: 'dvBarEnlarge', template: '<svg />' }),
  dvDetails: defineComponent({ name: 'dvDetails', template: '<svg />' }),
  icon_params_setting: defineComponent({ name: 'icon_params_setting', template: '<svg />' }),
  dvBarUnLinkage: defineComponent({ name: 'dvBarUnLinkage', template: '<svg />' }),
  database: defineComponent({ name: 'database', template: '<svg />' }),
  icon_more_outlined: defineComponent({ name: 'icon_more_outlined', template: '<svg />' }),
  dvPreviewDownload: defineComponent({ name: 'dvPreviewDownload', template: '<svg />' })
}

const baseElement = {
  id: 'view-1',
  component: 'UserView',
  innerType: 'table',
  x: 1,
  sizeX: 12
}

const mountComponent = (props: Record<string, unknown> = {}) =>
  shallowMount(ComponentEditBar, {
    props: {
      element: { ...baseElement },
      index: 0,
      showPosition: 'canvas',
      canvasId: 'canvas-main',
      ...props
    },
    global: { stubs }
  })

describe('ComponentEditBar', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.batchOptStatus = ref(false)
    mocks.pcMatrixCount = ref({ x: 12 })
    mocks.curComponent = ref({ id: 'view-1', innerType: 'table', editing: false })
    mocks.componentData = ref([])
    mocks.canvasViewInfo = ref({
      'view-1': {
        dataFrom: 'manual',
        calParams: [1],
        type: 'rich-text',
        curFields: [{ sourceFieldName: 'Field Name' }]
      }
    })
    mocks.mobileInPc = ref(false)
    mocks.dvInfo = ref({ weight: null, ext: null, type: 'dashboard', name: 'Demo' })
    mocks.isPopWindow = ref(false)
    mocks.hiddenListStatus = ref(false)
    mocks.isMobile = false
    mocks.isMainCanvas = true
  })

  it('renders right-inner class at canvas edge when hidden icon is not shown', () => {
    const wrapper = mountComponent()

    expect(wrapper.classes()).toContain('bar-main-right-inner')
  })

  it('switches to left-inner class when hidden list icon is shown on main canvas', () => {
    mocks.hiddenListStatus.value = true
    const wrapper = mountComponent()

    expect(wrapper.classes()).toContain('bar-main-left-inner')
  })

  it('toggles multiplexing selection through exposed method', () => {
    const wrapper = mountComponent({ showPosition: 'multiplexing' })

    ;(wrapper.vm as any).multiplexingCheckOut()
    ;(wrapper.vm as any).multiplexingCheckOut()

    expect(mocks.addCurMultiplexingComponent).toHaveBeenCalledWith({
      component: expect.objectContaining({ id: 'view-1' }),
      componentId: 'view-1'
    })
    expect(mocks.removeCurMultiplexingComponentWithId).toHaveBeenCalledWith('view-1')
  })

  it('toggles batch selection through exposed method in batch mode', () => {
    const wrapper = mountComponent({ showPosition: 'batchOpt' })

    ;(wrapper.vm as any).batchOptCheckOut()
    ;(wrapper.vm as any).batchOptCheckOut()

    expect(mocks.addCurBatchComponent).toHaveBeenCalledWith(
      expect.objectContaining({ id: 'view-1' })
    )
    expect(mocks.removeCurBatchComponentWithId).toHaveBeenCalledWith('view-1')
  })

  it('shows rich text fields popover when editing rich text content', async () => {
    mocks.curComponent.value = { id: 'view-1', innerType: 'rich-text', editing: true }
    const wrapper = mountComponent({
      showPosition: 'canvas',
      element: { ...baseElement, component: 'UserView', innerType: 'rich-text' }
    })

    await nextTick()

    expect(wrapper.findComponent({ name: 'FieldsList' }).exists()).toBe(true)
  })
})
