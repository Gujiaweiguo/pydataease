import { defineComponent, ref } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  canvasStyleData: null as any,
  recordSnapshotCache: vi.fn(),
  setCurrentFont: vi.fn(),
  adaptTitleFontFamilyAll: vi.fn()
}))

vi.mock('pinia', () => ({
  storeToRefs: (store: Record<string, unknown>) => store
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => key })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({ canvasStyleData: mocks.canvasStyleData })
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: mocks.recordSnapshotCache })
}))

vi.mock('@/store/modules/appearance', () => ({
  useAppearanceStoreWithOut: () => ({
    fontList: [{ name: 'CustomFont' }],
    setCurrentFont: mocks.setCurrentFont
  })
}))

vi.mock('@/views/chart/components/editor/util/chart', () => ({
  CHART_FONT_FAMILY_ORIGIN: [{ name: 'Arial', value: 'Arial' }]
}))

vi.mock('@/utils/canvasStyle', () => ({
  adaptTitleFontFamilyAll: mocks.adaptTitleFontFamilyAll
}))

vi.mock('@/utils/ModelUtil', () => ({
  isDesktop: () => false
}))

vi.mock('element-plus-secondary', () => ({
  ElFormItem: defineComponent({
    name: 'ElFormItem',
    props: ['label'],
    template: '<div class="form-item" :data-label="label"><slot /></div>'
  }),
  ElIcon: defineComponent({ name: 'ElIcon', template: '<i><slot /></i>' })
}))

import CanvasBaseSetting from '@/components/visualization/CanvasBaseSetting.vue'

const stubs = {
  ElForm: defineComponent({ name: 'ElForm', template: '<form><slot /></form>' }),
  ElSelect: defineComponent({
    name: 'ElSelect',
    props: ['modelValue'],
    emits: ['update:modelValue', 'change'],
    template:
      '<select class="select-stub" :value="modelValue" @change="$emit(\'update:modelValue\', $event.target.value); $emit(\'change\', $event.target.value)"><slot /></select>'
  }),
  ElOption: defineComponent({
    name: 'ElOption',
    props: ['label', 'value'],
    template: '<option :value="value">{{ label }}</option>'
  }),
  ElCheckbox: defineComponent({
    name: 'ElCheckbox',
    props: ['modelValue'],
    emits: ['update:modelValue', 'change'],
    template:
      '<input class="checkbox-stub" type="checkbox" :checked="modelValue" @change="$emit(\'update:modelValue\', $event.target.checked); $emit(\'change\', $event.target.checked)" />'
  }),
  ElTooltip: defineComponent({
    name: 'ElTooltip',
    template: '<div><slot /><slot name="content" /></div>'
  }),
  ElIcon: defineComponent({ name: 'ElIcon', template: '<i><slot /></i>' }),
  Icon: defineComponent({ name: 'Icon', template: '<span><slot /></span>' }),
  icon_info_outlined: defineComponent({ name: 'icon_info_outlined', template: '<svg />' })
}

describe('CanvasBaseSetting', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // ref already imported at top
    mocks.canvasStyleData = ref({
      fontFamily: 'Arial',
      popupButtonAvailable: false,
      suspensionButtonAvailable: true,
      dashboard: { showGrid: false }
    })
  })

  it('renders font options from defaults and appearance store', () => {
    const wrapper = mount(CanvasBaseSetting, { global: { stubs } })

    expect(wrapper.text()).toContain('Arial')
    expect(wrapper.text()).toContain('CustomFont')
  })

  it('updates current font and records snapshot on font change', async () => {
    const wrapper = mount(CanvasBaseSetting, { global: { stubs } })

    await wrapper.get('.select-stub').setValue('CustomFont')

    expect(mocks.setCurrentFont).toHaveBeenCalledWith('CustomFont')
    expect(mocks.adaptTitleFontFamilyAll).toHaveBeenCalledWith('CustomFont')
    expect(mocks.recordSnapshotCache).toHaveBeenCalledWith('renderChart')
  })

  it('records snapshot when theme-related checkboxes change', async () => {
    const wrapper = mount(CanvasBaseSetting, { global: { stubs } })

    await wrapper.findAll('.checkbox-stub')[0].setValue(true)

    expect(mocks.recordSnapshotCache).toHaveBeenCalledWith('onThemeChange')
  })
})
