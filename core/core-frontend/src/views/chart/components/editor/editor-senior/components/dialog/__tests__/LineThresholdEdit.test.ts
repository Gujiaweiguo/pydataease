import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (key: string) => key }) }))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#ff0000', '#00ff00']
}))
vi.mock('@/utils/attr', () => ({
  fieldType: { 0: 'text', 1: 'time', 2: 'value', 3: 'value', 4: 'value' }
}))
vi.mock('@/components/icon-group/field-list', () => ({ iconFieldMap: {} }))

import LineThresholdEdit from '../LineThresholdEdit.vue'

const globalStubs = {
  ElCol: { template: '<div class="col-stub"><slot /></div>' },
  ElRow: { template: '<div class="row-stub"><slot /></div>' },
  ElFormItem: { template: '<div class="form-item-stub"><slot /></div>' },
  ElSelect: { props: ['modelValue'], template: '<select class="select-stub"><slot /></select>' },
  ElOption: {
    props: ['label', 'value'],
    template: '<option class="option-stub" :value="value">{{ label }}</option>'
  },
  ElOptionGroup: {
    props: ['label'],
    template: '<optgroup class="option-group-stub"><slot /></optgroup>'
  },
  ElInputNumber: {
    props: ['modelValue'],
    template: '<input class="input-number-stub" type="number" />'
  },
  ElInput: { props: ['modelValue'], template: '<input class="input-stub" />' },
  ElColorPicker: { props: ['modelValue'], template: '<div class="color-picker-stub" />' },
  ElButton: { template: '<button class="button-stub"><slot /><slot name="icon" /></button>' },
  ElIcon: { template: '<i class="icon-stub"><slot /></i>' },
  Icon: { template: '<span class="vant-icon-stub"><slot /></span>' }
}

const yAxisFields = [
  { id: 'y1', name: 'Revenue', deType: 2 },
  { id: 'y2', name: 'Cost', deType: 2 }
]

const mountComponent = (threshold: any[] = []) =>
  shallowMount(LineThresholdEdit, {
    props: {
      chart: { type: 'bar', yAxis: yAxisFields } as any,
      threshold
    },
    global: { stubs: globalStubs }
  })

describe('LineThresholdEdit', () => {
  it('initializes thresholdArr from the threshold prop', () => {
    const threshold = [
      {
        fieldId: 'y1',
        field: yAxisFields[0],
        conditions: [{ term: 'gt', value: '100', color: '#ff0000ff' }]
      }
    ]
    const wrapper = mountComponent(threshold)

    expect((wrapper.vm as any).state.thresholdArr).toHaveLength(1)
    expect((wrapper.vm as any).state.thresholdArr[0].fieldId).toBe('y1')
  })

  it('adds a new threshold entry and emits the change', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.addThreshold()

    expect(vm.state.thresholdArr).toHaveLength(1)
    expect(wrapper.emitted('onLineThresholdChange')).toBeDefined()
  })

  it('removes a threshold entry by index', () => {
    const threshold = [
      { fieldId: 'y1', field: yAxisFields[0], conditions: [] },
      { fieldId: 'y2', field: yAxisFields[1], conditions: [] }
    ]
    const wrapper = mountComponent(threshold)
    const vm = wrapper.vm as any

    vm.removeThreshold(0)

    expect(vm.state.thresholdArr).toHaveLength(1)
    expect(vm.state.thresholdArr[0].fieldId).toBe('y2')
  })

  it('adds a condition to an existing threshold entry', () => {
    const threshold = [{ fieldId: 'y1', field: yAxisFields[0], conditions: [] }]
    const wrapper = mountComponent(threshold)
    const vm = wrapper.vm as any

    vm.addConditions(vm.state.thresholdArr[0])

    expect(vm.state.thresholdArr[0].conditions).toHaveLength(1)
    expect(vm.state.thresholdArr[0].conditions[0].term).toBe('lt')
  })

  it('removes a condition from a threshold entry', () => {
    const threshold = [
      { fieldId: 'y1', field: yAxisFields[0], conditions: [{ term: 'gt' }, { term: 'lt' }] }
    ]
    const wrapper = mountComponent(threshold)
    const vm = wrapper.vm as any

    vm.removeCondition(vm.state.thresholdArr[0], 0)

    expect(vm.state.thresholdArr[0].conditions).toHaveLength(1)
    expect(vm.state.thresholdArr[0].conditions[0].term).toBe('lt')
  })
})
