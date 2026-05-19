import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (key: string) => key }) }))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#ff0000', '#00ff00'],
  DEFAULT_FUNCTION_CFG: {},
  DEFAULT_THRESHOLD: {
    enable: false,
    gaugeThreshold: '',
    liquidThreshold: '',
    labelThreshold: [],
    textLabelThreshold: [],
    tableThreshold: [],
    lineThreshold: []
  },
  DEFAULT_ASSIST_LINE_CFG: { enable: false, assistLine: [] }
}))
vi.mock('@/utils/attr', () => ({
  fieldType: { 0: 'text', 1: 'time', 2: 'value', 3: 'value', 4: 'value' }
}))
vi.mock('@/components/icon-group/field-list', () => ({ iconFieldMap: {} }))

import AssistLineEdit from '../AssistLineEdit.vue'

const globalStubs = {
  ElRow: { template: '<div class="row-stub"><slot /></div>' },
  ElCol: { props: ['span'], template: '<div class="col-stub"><slot /></div>' },
  ElInput: { props: ['modelValue'], template: '<input class="input-stub" />' },
  ElInputNumber: {
    props: ['modelValue'],
    template: '<input class="input-number-stub" type="number" />'
  },
  ElSelect: { props: ['modelValue'], template: '<select class="select-stub"><slot /></select>' },
  ElOption: {
    props: ['label', 'value'],
    template: '<option class="option-stub" :value="value">{{ label }}</option>'
  },
  ElColorPicker: { props: ['modelValue'], template: '<div class="color-picker-stub" />' },
  ElTooltip: { template: '<div class="tooltip-stub"><slot /></div>' },
  ElButton: { template: '<button class="button-stub"><slot /><slot name="icon" /></button>' },
  ElIcon: { template: '<i class="icon-stub"><slot /></i>' },
  Icon: { template: '<span class="vant-icon-stub"><slot /></span>' }
}

const quotaFields = [
  { id: 'qf1', name: 'Sales', summary: 'sum', deType: 2 },
  { id: 'qf2', name: 'Profit', summary: 'avg', deType: 2 }
]

const mountComponent = (line: any[] = [], useQuotaExt = false) =>
  shallowMount(AssistLineEdit, {
    props: {
      chart: { type: 'bar' },
      line,
      quotaFields,
      quotaExtFields: [],
      useQuotaExt
    },
    global: {
      stubs: globalStubs
    }
  })

describe('AssistLineEdit', () => {
  it('initializes lineArr from the line prop', () => {
    const line = [
      {
        name: 'Target',
        field: '0',
        value: '10',
        lineType: 'solid',
        color: '#ff0000',
        fontSize: '10'
      }
    ]
    const wrapper = mountComponent(line)

    expect((wrapper.vm as any).state.lineArr).toHaveLength(1)
    expect((wrapper.vm as any).state.lineArr[0].name).toBe('Target')
  })

  it('adds a new line with default values', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.addLine()

    expect(vm.state.lineArr).toHaveLength(1)
    expect(vm.state.lineArr[0].field).toBe('0')
    expect(wrapper.emitted('onAssistLineChange')).toBeDefined()
  })

  it('removes a line by index', () => {
    const line = [
      { name: 'A', field: '0', value: '5', lineType: 'solid', color: '#ff0000', fontSize: '10' },
      { name: 'B', field: '0', value: '10', lineType: 'dashed', color: '#00ff00', fontSize: '12' }
    ]
    const wrapper = mountComponent(line)
    const vm = wrapper.vm as any

    vm.removeLine(0)

    expect(vm.state.lineArr).toHaveLength(1)
    expect(vm.state.lineArr[0].name).toBe('B')
  })

  it('clears fieldId when the referenced field no longer exists', () => {
    const line = [
      {
        name: 'Old',
        field: '1',
        fieldId: 'deleted-field',
        yAxisType: 'left',
        lineType: 'solid',
        color: '#ff0000',
        fontSize: '10'
      }
    ]
    const wrapper = mountComponent(line)

    expect((wrapper.vm as any).state.lineArr[0].fieldId).toBeUndefined()
  })

  it('computes fontSizeList from 10 to 60 in steps of 2', () => {
    const wrapper = mountComponent()

    const list = (wrapper.vm as any).fontSizeList
    expect(list).toHaveLength(26)
    expect(list[0]).toEqual({ name: '10', value: '10' })
    expect(list[25]).toEqual({ name: '60', value: '60' })
  })
})
