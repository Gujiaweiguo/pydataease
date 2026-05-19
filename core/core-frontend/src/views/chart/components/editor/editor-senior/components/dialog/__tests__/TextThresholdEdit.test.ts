import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (key: string) => key }) }))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#ff0000', '#00ff00']
}))

import TextThresholdEdit from '../TextThresholdEdit.vue'

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
  ElSpace: { template: '<div class="space-stub"><slot /></div>' },
  Icon: { template: '<span class="vant-icon-stub"><slot /></span>' }
}

const mountComponent = (threshold: any[] = []) =>
  shallowMount(TextThresholdEdit, {
    props: { threshold },
    global: { stubs: globalStubs }
  })

describe('TextThresholdEdit', () => {
  it('initializes thresholdArr from the threshold prop', () => {
    const threshold = [
      { term: 'eq', value: '0', color: '#ff0000ff', backgroundColor: '#fff', min: '0', max: '1' }
    ]
    const wrapper = mountComponent(threshold)

    expect((wrapper.vm as any).state.thresholdArr).toHaveLength(1)
    expect((wrapper.vm as any).state.thresholdArr[0].term).toBe('eq')
  })

  it('adds a default threshold entry and emits the change', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.addThreshold()

    expect(vm.state.thresholdArr).toHaveLength(1)
    expect(vm.state.thresholdArr[0].term).toBe('eq')
    expect(wrapper.emitted('onLabelThresholdChange')).toBeDefined()
  })

  it('removes a threshold entry by index', () => {
    const threshold = [
      { term: 'eq', value: '0', color: '#ff0000ff', backgroundColor: '#fff', min: '0', max: '1' },
      { term: 'gt', value: '5', color: '#00ff00ff', backgroundColor: '#000', min: '0', max: '1' }
    ]
    const wrapper = mountComponent(threshold)
    const vm = wrapper.vm as any

    vm.removeThreshold(0)

    expect(vm.state.thresholdArr).toHaveLength(1)
    expect(vm.state.thresholdArr[0].term).toBe('gt')
  })

  it('emits the updated threshold array on changeThreshold', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.changeThreshold()

    expect(wrapper.emitted('onLabelThresholdChange')).toEqual([[vm.state.thresholdArr]])
  })

  it('creates a deep copy of the threshold prop to avoid mutation', () => {
    const threshold = [{ term: 'eq', value: '10' }]
    const wrapper = mountComponent(threshold)
    const vm = wrapper.vm as any

    vm.state.thresholdArr[0].value = '20'

    expect(threshold[0].value).toBe('10')
  })
})
