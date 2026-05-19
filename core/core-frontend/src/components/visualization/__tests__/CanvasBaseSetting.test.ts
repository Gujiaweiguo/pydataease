import { defineComponent, ref } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  canvasStyleData: null as any,
  recordSnapshotCache: vi.fn(),
  setCurrentFont: vi.fn(),
  adaptTitleFontFamilyAll: vi.fn(),
  isDesktop: false
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
  CHART_FONT_FAMILY_ORIGIN: [{ name: 'SerifDisplay', value: 'SerifDisplay' }]
}))

vi.mock('@/utils/canvasStyle', () => ({
  adaptTitleFontFamilyAll: mocks.adaptTitleFontFamilyAll
}))

vi.mock('@/utils/ModelUtil', () => ({
  isDesktop: () => mocks.isDesktop
}))

import CanvasBaseSetting from '../CanvasBaseSetting.vue'

const stubs = {
  ElForm: defineComponent({ name: 'ElForm', template: '<form><slot /></form>' }),
  ElFormItem: defineComponent({
    name: 'ElFormItem',
    props: ['label'],
    template: '<div class="form-item" :data-label="label"><slot /></div>'
  }),
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
    mocks.isDesktop = false
    mocks.canvasStyleData = ref({
      fontFamily: 'SerifDisplay',
      popupButtonAvailable: false,
      suspensionButtonAvailable: true,
      dashboard: { showGrid: false }
    })
  })

  it('renders font options from default and appearance font lists', () => {
    const wrapper = shallowMount(CanvasBaseSetting, { global: { stubs } })

    const options = wrapper.findAll('option').map(option => option.text())
    expect(options).toEqual(expect.arrayContaining(['SerifDisplay', 'CustomFont']))
  })

  it('shows all three checkbox controls in non-desktop mode', () => {
    const wrapper = shallowMount(CanvasBaseSetting, { global: { stubs } })

    expect(wrapper.findAll('.checkbox-stub')).toHaveLength(3)
  })

  it('updates font settings and records a render snapshot on font change', async () => {
    const setPropertySpy = vi.spyOn(document.documentElement.style, 'setProperty')
    const wrapper = shallowMount(CanvasBaseSetting, { global: { stubs } })

    await wrapper.get('.select-stub').setValue('CustomFont')

    expect(mocks.setCurrentFont).toHaveBeenCalledWith('CustomFont')
    expect(setPropertySpy).toHaveBeenCalledWith('--de-canvas_custom_font', 'CustomFont')
    expect(mocks.adaptTitleFontFamilyAll).toHaveBeenCalledWith('CustomFont')
    expect(mocks.recordSnapshotCache).toHaveBeenCalledWith('renderChart')
  })

  it('records theme snapshot when a checkbox changes', async () => {
    const wrapper = shallowMount(CanvasBaseSetting, { global: { stubs } })

    await wrapper.findAll('.checkbox-stub')[0].setValue(true)

    expect(mocks.recordSnapshotCache).toHaveBeenCalledWith('onThemeChange')
  })
})
