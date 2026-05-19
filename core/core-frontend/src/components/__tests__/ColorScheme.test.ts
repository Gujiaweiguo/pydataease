import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

const { hideMock, showMock } = vi.hoisted(() => ({
  hideMock: vi.fn(),
  showMock: vi.fn()
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => `translated:${key}`
  })
}))

vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_CASES: [
    {
      colors: ['#ff0000', '#00ff00'],
      name: 'Warm',
      value: 'warm'
    },
    {
      colors: ['#0000ff', '#ffff00'],
      name: 'Cool',
      value: 'cool'
    }
  ],
  COLOR_PANEL: ['#111111', '#222222']
}))

import ColorScheme from '../color-scheme/src/ColorScheme.vue'

const ElSelectStub = defineComponent({
  name: 'ElSelect',
  emits: ['update:modelValue', 'change'],
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: ''
    }
  },
  template:
    '<select class="select-stub" :value="modelValue" :data-placeholder="placeholder" @change="$emit(\'update:modelValue\', $event.target.value); $emit(\'change\')"><slot /></select>'
})

const ElOptionStub = defineComponent({
  name: 'ElOption',
  props: {
    label: {
      type: String,
      default: ''
    },
    value: {
      type: String,
      default: ''
    }
  },
  template: '<option class="option-stub" :value="value">{{ label }}</option>'
})

const ElButtonStub = defineComponent({
  name: 'ElButton',
  emits: ['click'],
  template:
    '<button type="button" class="button-stub" @click="$emit(\'click\')"><span class="icon-slot"><slot name="icon" /></span><slot /></button>'
})

const ElColorPickerStub = defineComponent({
  name: 'ElColorPicker',
  emits: ['update:modelValue', 'change'],
  props: {
    modelValue: {
      type: String,
      default: ''
    }
  },
  setup() {
    return {
      hide: hideMock,
      show: showMock
    }
  },
  template:
    '<input class="color-picker-stub" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" @change="$emit(\'change\')" />'
})

const mountComponent = () =>
  mount(ColorScheme, {
    global: {
      stubs: {
        ElButton: ElButtonStub,
        ElColorPicker: ElColorPickerStub,
        ElOption: ElOptionStub,
        ElSelect: ElSelectStub,
        Icon: {
          template: '<span class="icon-stub"><slot /></span>'
        }
      }
    }
  })

describe('ColorScheme', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders translated labels and keeps the custom editor hidden by default', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('translated:chart.color_case')
    expect(wrapper.get('.select-stub').attributes('data-placeholder')).toBe(
      'translated:chart.pls_slc_color_case'
    )
    expect((wrapper.get('.color-custom').element.parentElement as HTMLElement).style.display).toBe(
      'none'
    )
  })

  it('updates the preview colors when a preset is selected', async () => {
    const wrapper = mountComponent()

    await wrapper.get('.select-stub').setValue('cool')

    const previewItems = wrapper.findAll('.item-select')
    expect(previewItems).toHaveLength(2)
    expect((previewItems[0].element as HTMLElement).style.backgroundColor).toBe('#0000ff')
    expect((previewItems[1].element as HTMLElement).style.backgroundColor).toBe('#ffff00')
  })

  it('supports custom editing and reset for the selected color scheme', async () => {
    const wrapper = mountComponent()

    await wrapper.get('.select-stub').setValue('warm')
    await wrapper.find('.button-stub').trigger('click')
    await wrapper.findAll('.color-item')[0].trigger('click')
    vi.runAllTimers()

    await wrapper.get('.color-picker-stub').setValue('#123456')
    expect((wrapper.findAll('.color-item')[0].element as HTMLElement).style.backgroundColor).toBe(
      '#123456'
    )
    expect(showMock).toHaveBeenCalledTimes(1)

    await wrapper.findAll('.button-stub')[1].trigger('click')
    expect((wrapper.findAll('.color-item')[0].element as HTMLElement).style.backgroundColor).toBe(
      '#ff0000'
    )
    expect(hideMock).toHaveBeenCalled()
  })
})
