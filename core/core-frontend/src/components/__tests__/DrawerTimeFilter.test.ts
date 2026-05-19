import { defineComponent, nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => `t:${key}`
  })
}))

import DrawerTimeFilter from '../drawer-filter/src/DrawerTimeFilter.vue'

const ElDatePickerStub = defineComponent({
  name: 'ElDatePicker',
  props: {
    modelValue: {
      type: Array,
      default: () => []
    },
    type: {
      type: String,
      default: ''
    },
    rangeSeparator: {
      type: String,
      default: ''
    },
    startPlaceholder: {
      type: String,
      default: ''
    },
    endPlaceholder: {
      type: String,
      default: ''
    },
    format: {
      type: String,
      default: ''
    },
    valueFormat: {
      type: String,
      default: ''
    },
    size: {
      type: String,
      default: ''
    },
    placement: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue', 'change'],
  template:
    '<div class="el-date-picker-stub" :data-model-value="JSON.stringify(modelValue)" :data-type="type" :data-range-separator="rangeSeparator" :data-start-placeholder="startPlaceholder" :data-end-placeholder="endPlaceholder" :data-format="format" :data-value-format="valueFormat" :data-size="size" :data-placement="placement"></div>'
})

const mountComponent = (props?: Record<string, unknown>) =>
  mount(DrawerTimeFilter, {
    props: {
      title: 'Time Filter',
      ...props
    },
    global: {
      stubs: {
        ElDatePicker: ElDatePickerStub
      }
    }
  })

describe('DrawerTimeFilter', () => {
  it('renders translated default date-range configuration', () => {
    const wrapper = mountComponent()
    const picker = wrapper.getComponent(ElDatePickerStub)

    expect(wrapper.text()).toContain('Time Filter')
    expect(picker.props('type')).toBe('datetime')
    expect(picker.props('startPlaceholder')).toBe('t:datasource.start_time')
    expect(picker.props('endPlaceholder')).toBe('t:datasource.end_time')
  })

  it('merges custom picker properties into the rendered control', () => {
    const wrapper = mountComponent({
      property: {
        showType: 'daterange',
        rangeSeparator: '~',
        size: 'small',
        placement: 'top-end'
      }
    })
    const picker = wrapper.getComponent(ElDatePickerStub)

    expect(picker.props('type')).toBe('daterange')
    expect(picker.props('rangeSeparator')).toBe('~')
    expect(picker.props('size')).toBe('small')
    expect(picker.props('placement')).toBe('top-end')
  })

  it('emits and clears selected date ranges', async () => {
    const wrapper = mountComponent()
    const picker = wrapper.getComponent(ElDatePickerStub)
    const value = ['2026-01-01 00:00:00', '2026-01-02 00:00:00']

    picker.vm.$emit('update:modelValue', value)
    picker.vm.$emit('change', value)
    await nextTick()
    expect(wrapper.emitted('filter-change')?.at(-1)).toEqual([value])
    ;(wrapper.vm as unknown as { clear: () => void }).clear()
    await nextTick()
    expect(wrapper.get('.el-date-picker-stub').attributes('data-model-value')).toBe('[]')
  })
})
