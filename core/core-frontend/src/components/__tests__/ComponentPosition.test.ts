import { defineComponent, ref } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mockState = vi.hoisted(() => ({
  recordSnapshotCache: vi.fn(),
  groupSizeStyleAdaptor: vi.fn(),
  groupStyleRevert: vi.fn(),
  isGroupCanvas: vi.fn(() => false),
  isTabCanvas: vi.fn(() => false)
}))

const dvMainRefs = vi.hoisted(() => ({
  curComponent: null as any,
  canvasStyleData: null as any
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => `t:${key}` })
}))

vi.mock('@/utils/attr', () => ({
  positionData: [
    { key: 'width', label: 'W', min: 0, max: 1000, step: 1 },
    { key: 'height', label: 'H', min: 0, max: 1000, step: 1 },
    { key: 'top', label: 'T', min: 0, max: 1000, step: 1 },
    { key: 'left', label: 'L', min: 0, max: 1000, step: 1 }
  ]
}))

vi.mock('@/utils/style', () => ({
  groupSizeStyleAdaptor: mockState.groupSizeStyleAdaptor,
  groupStyleRevert: mockState.groupStyleRevert
}))

vi.mock('@/utils/canvasUtils', () => ({
  isGroupCanvas: mockState.isGroupCanvas,
  isTabCanvas: mockState.isTabCanvas
}))

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: (store: Record<string, unknown>) => store
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: mockState.recordSnapshotCache
  })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => {
  const curComponent = ref({
    component: 'VText',
    canvasId: 'canvas-main',
    isLock: false,
    maintainRadio: false,
    aspectRatio: 2,
    style: {
      width: 200,
      height: 100,
      top: 40,
      left: 20
    }
  })
  const canvasStyleData = ref({ scale: 100 })
  dvMainRefs.curComponent = curComponent
  dvMainRefs.canvasStyleData = canvasStyleData

  return {
    dvMainStoreWithOut: () => ({
      curComponent,
      canvasStyleData
    })
  }
})

import ComponentPosition from '@/components/visualization/common/ComponentPosition.vue'

const ElInputNumberStub = defineComponent({
  name: 'ElInputNumber',
  props: ['modelValue', 'disabled'],
  emits: ['change'],
  template: '<div class="input-number-stub" :data-value="String(modelValue)"></div>'
})

const mountComponent = () => {
  document.querySelector = vi.fn(() => ({
    offsetWidth: 800,
    offsetHeight: 600
  })) as typeof document.querySelector

  return mount(ComponentPosition, {
    props: {
      themes: 'light'
    },
    global: {
      stubs: {
        ElForm: defineComponent({ name: 'ElForm', template: '<form><slot /></form>' }),
        ElRow: defineComponent({ name: 'ElRow', template: '<div class="row-stub"><slot /></div>' }),
        ElCol: defineComponent({ name: 'ElCol', template: '<div class="col-stub"><slot /></div>' }),
        ElFormItem: defineComponent({
          name: 'ElFormItem',
          template: '<div class="form-item-stub"><slot /></div>'
        }),
        ElInputNumber: ElInputNumberStub,
        ElCheckbox: defineComponent({
          name: 'ElCheckbox',
          props: ['modelValue'],
          emits: ['change'],
          template: '<label class="checkbox-stub"><slot /></label>'
        })
      }
    }
  })
}

describe('ComponentPosition', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    dvMainRefs.curComponent.value = {
      component: 'VText',
      canvasId: 'canvas-main',
      isLock: false,
      maintainRadio: false,
      aspectRatio: 2,
      style: {
        width: 200,
        height: 100,
        top: 40,
        left: 20
      }
    }
    dvMainRefs.canvasStyleData.value = { scale: 100 }
  })

  it('renders an input number for each supported position key', () => {
    const wrapper = mountComponent()

    expect(wrapper.findAllComponents(ElInputNumberStub)).toHaveLength(4)
  })

  it('updates the current component style and records a snapshot on position change', async () => {
    const wrapper = mountComponent()

    await wrapper.findAllComponents(ElInputNumberStub)[0].vm.$emit('change', 320)

    expect(dvMainRefs.curComponent.value.style.width).toBe(200)
    expect(mockState.recordSnapshotCache).toHaveBeenCalledWith('onPositionChange')
  })

  it('keeps the aspect ratio when maintainRadio is enabled', async () => {
    dvMainRefs.curComponent.value.maintainRadio = true
    const wrapper = mountComponent()

    await wrapper.findAllComponents(ElInputNumberStub)[0].vm.$emit('change', 300)

    expect(dvMainRefs.curComponent.value.style.height).toBe(100)
    expect(mockState.recordSnapshotCache).toHaveBeenCalledWith('onPositionChange')
  })
})
