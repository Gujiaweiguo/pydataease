import { defineComponent, nextTick, ref } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { multFieldValuesForPermissionsMock, timeDialogInitMock } = vi.hoisted(() => ({
  multFieldValuesForPermissionsMock: vi.fn(async () => ({ data: ['North', '', 'South'] })),
  timeDialogInitMock: vi.fn()
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => `t:${key}` })
}))

vi.mock('@/api/dataset', () => ({
  multFieldValuesForPermissions: multFieldValuesForPermissionsMock
}))

vi.mock('@/components/icon-group/field-list.js', () => ({
  iconFieldMap: {
    text: 'span',
    time: 'span',
    value: 'span',
    location: 'span'
  }
}))

import FilterFiled from '../auth-tree/FilterFiled.vue'

const ElDropdownStub = defineComponent({
  name: 'ElDropdown',
  template: '<div class="dropdown-stub"><slot /><slot name="dropdown" /></div>'
})

const ElDropdownMenuStub = defineComponent({
  name: 'ElDropdownMenu',
  template: '<div class="dropdown-menu-stub"><slot /></div>'
})

const ElInputStub = defineComponent({
  name: 'ElInput',
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    },
    value: {
      type: [String, Number],
      default: ''
    },
    readonly: {
      type: Boolean,
      default: false
    }
  },
  emits: ['click', 'input', 'update:modelValue'],
  template: `
    <input
      class="el-input-stub"
      :class="$attrs.class"
      :readonly="readonly"
      :value="modelValue || value"
      @click="$emit('click')"
      @input="$emit('update:modelValue', $event.target.value); $emit('input', $event.target.value)"
    />
  `
})

const ElSelectStub = defineComponent({
  name: 'ElSelect',
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    }
  },
  emits: ['change', 'update:modelValue'],
  template: `
    <select
      class="el-select-stub"
      :class="$attrs.class"
      :value="modelValue"
      @change="$emit('update:modelValue', $event.target.value); $emit('change', $event.target.value)"
    >
      <slot />
    </select>
  `
})

const ElOptionStub = defineComponent({
  name: 'ElOption',
  props: {
    value: {
      type: [String, Number],
      default: ''
    },
    label: {
      type: String,
      default: ''
    }
  },
  template: '<option :value="value">{{ label }}<slot /></option>'
})

const ElInputNumberStub = defineComponent({
  name: 'ElInputNumber',
  template: '<input class="el-input-number-stub" />'
})

const ElPopoverStub = defineComponent({
  name: 'ElPopover',
  template: '<div class="popover-stub"><slot name="reference" /><slot /></div>'
})

const ElCheckboxStub = defineComponent({
  name: 'ElCheckbox',
  props: {
    modelValue: {
      type: [Boolean, Array],
      default: false
    },
    label: {
      type: String,
      default: ''
    }
  },
  emits: ['change', 'update:modelValue'],
  template:
    '<label class="checkbox-stub"><input type="checkbox" @change="$emit(\'update:modelValue\', true); $emit(\'change\', true)" /><slot />{{ label }}</label>'
})

const ElCheckboxGroupStub = defineComponent({
  name: 'ElCheckboxGroup',
  template: '<div class="checkbox-group-stub"><slot /></div>'
})

const ElScrollbarStub = defineComponent({
  name: 'ElScrollbar',
  template: '<div class="scrollbar-stub"><slot /></div>'
})

const ElIconStub = defineComponent({
  name: 'ElIcon',
  template: '<i class="icon-stub"><slot /></i>'
})

const ElButtonStub = defineComponent({
  name: 'ElButton',
  emits: ['click'],
  template:
    '<button class="el-button-stub" type="button" @click="$emit(\'click\')"><slot /></button>'
})

const IconStub = defineComponent({
  name: 'Icon',
  template: '<span class="custom-icon-stub"><slot /></span>'
})

const TimeSetDialogStub = defineComponent({
  name: 'TimeSetDialog',
  methods: {
    init(type: string, value: string) {
      timeDialogInitMock(type, value)
    }
  },
  template: '<div class="time-dialog-stub" />'
})

const mountComponent = (item: Record<string, unknown>, authTargetType = '') =>
  shallowMount(FilterFiled, {
    props: {
      index: 0,
      item
    },
    global: {
      provide: {
        filedList: ref({
          one: { id: 'field_1', name: 'Region', deType: 0 },
          two: { id: 'field_2', name: 'Created At', deType: 1 }
        }),
        getAuthTargetType: { authTargetType }
      },
      stubs: {
        ElCheckbox: ElCheckboxStub,
        ElCheckboxGroup: ElCheckboxGroupStub,
        ElButton: ElButtonStub,
        ElDropdown: ElDropdownStub,
        ElDropdownMenu: ElDropdownMenuStub,
        ElIcon: ElIconStub,
        ElInput: ElInputStub,
        ElInputNumber: ElInputNumberStub,
        ElOption: ElOptionStub,
        ElPopover: ElPopoverStub,
        ElScrollbar: ElScrollbarStub,
        ElSelect: ElSelectStub,
        Icon: IconStub,
        TimeSetDialog: TimeSetDialogStub
      }
    }
  })

describe('FilterFiled', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('uses the narrow width before a field is selected', () => {
    const wrapper = mountComponent({
      term: '',
      fieldId: '',
      filterType: '',
      deType: 0,
      enumValue: [],
      name: '',
      value: ''
    })

    expect((wrapper.get('.filed').element as HTMLElement).style.width).toBe('270px')
  })

  it('updates the bound item when a field is chosen from the dropdown', async () => {
    const item = {
      term: '',
      fieldId: '',
      filterType: '',
      deType: 0,
      enumValue: [],
      name: '',
      value: '',
      timeType: 'year'
    }
    const wrapper = mountComponent(item)

    await wrapper.findAll('.dimension li')[0].trigger('click')

    expect(item).toMatchObject({
      deType: 0,
      enumValue: [],
      fieldId: 'field_1',
      filterType: 'logic',
      name: 'Region',
      term: '',
      value: ''
    })
  })

  it('opens the time dialog for date fields', async () => {
    const wrapper = mountComponent({
      term: 'eq',
      fieldId: 'field_2',
      filterType: 'logic',
      deType: 1,
      enumValue: [],
      name: 'Created At',
      value: '2026',
      timeType: 'year'
    })

    await wrapper.find('.w70.mar5').trigger('click')

    expect(timeDialogInitMock).toHaveBeenCalledWith('year', '2026')
  })

  it('loads enum options for text fields that use enum filtering', async () => {
    mountComponent({
      term: '',
      fieldId: 'field_1',
      filterType: 'enum',
      deType: 0,
      enumValue: ['North'],
      name: 'Region',
      value: ''
    })

    await nextTick()
    await Promise.resolve()

    expect(multFieldValuesForPermissionsMock).toHaveBeenCalledWith({ fieldIds: ['field_1'] })
  })
})
