import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => `translated:${key}`
  })
}))

import DrawerTimeFilter from '../DrawerTimeFilter.vue'

const ElDatePickerStub = defineComponent({
  name: 'ElDatePicker',
  props: {
    modelValue: {
      type: Array,
      default: () => []
    },
    type: {
      type: String,
      default: 'datetime'
    },
    rangeSeparator: {
      type: String,
      default: '-'
    },
    startPlaceholder: {
      type: String,
      default: ''
    },
    endPlaceholder: {
      type: String,
      default: ''
    }
  },
  template:
    '<div class="date-picker-stub" :data-type="type" :data-range-sep="rangeSeparator">{{ startPlaceholder }} {{ rangeSeparator }} {{ endPlaceholder }}</div>'
})

const mountComponent = () =>
  mount(DrawerTimeFilter, {
    props: {
      title: 'Time Filter',
      property: {
        showType: 'datetime',
        rangeSeparator: '~',
        startPlaceholder: 'From',
        endPlaceholder: 'To',
        format: 'YYYY-MM-DD',
        valueFormat: 'YYYY-MM-DD',
        size: 'default',
        placement: 'bottom-end'
      }
    },
    global: {
      stubs: {
        ElDatePicker: ElDatePickerStub
      }
    }
  })

describe('DrawerTimeFilter', () => {
  it('renders the title', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('Time Filter')
  })

  it('renders date picker with correct type and placeholders', () => {
    const wrapper = mountComponent()

    const picker = wrapper.get('.date-picker-stub')
    expect(picker.attributes('data-type')).toBe('datetime')
    expect(picker.attributes('data-range-sep')).toBe('~')
    expect(wrapper.text()).toContain('From')
    expect(wrapper.text()).toContain('To')
  })

  it('exposes clear method', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as unknown as { clear: () => void }

    expect(typeof vm.clear).toBe('function')
  })
})
