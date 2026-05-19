import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (key: string) => key }) }))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#ff0000', '#00ff00']
}))

import TextLabelThresholdEdit from '../TextLabelThresholdEdit.vue'

const globalStubs = {
  ElCol: { template: '<div class="col-stub"><slot /></div>' },
  ElRow: { template: '<div class="row-stub"><slot /></div>' },
  ElSelect: { props: ['modelValue'], template: '<select class="select-stub"><slot /></select>' },
  ElOption: {
    props: ['label', 'value'],
    template: '<option class="option-stub" :value="value">{{ label }}</option>'
  },
  ElOptionGroup: {
    props: ['label'],
    template: '<optgroup class="option-group-stub"><slot /></optgroup>'
  },
  ElInput: { props: ['modelValue'], template: '<input class="input-stub" />' },
  ElColorPicker: { props: ['modelValue'], template: '<div class="color-picker-stub" />' },
  ElButton: { template: '<button class="button-stub"><slot /><slot name="icon" /></button>' },
  Icon: { template: '<span class="vant-icon-stub"><slot /></span>' }
}

const mountComponent = (threshold: any[] = []) =>
  shallowMount(TextLabelThresholdEdit, {
    props: { threshold },
    global: { stubs: globalStubs }
  })

describe('TextLabelThresholdEdit', () => {
  it('initializes thresholdArr from the threshold prop', () => {
    const threshold = [{ term: 'eq', value: 'Hello', color: '#ff0000ff' }]
    const wrapper = mountComponent(threshold)

    expect((wrapper.vm as any).state.thresholdArr).toHaveLength(1)
    expect((wrapper.vm as any).state.thresholdArr[0].term).toBe('eq')
  })

  it('adds a default text label threshold entry', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.addThreshold()

    expect(vm.state.thresholdArr).toHaveLength(1)
    expect(vm.state.thresholdArr[0].term).toBe('eq')
    expect(vm.state.thresholdArr[0].value).toBe('')
    expect(wrapper.emitted('onTextLabelThresholdChange')).toBeDefined()
  })

  it('removes a threshold entry by index', () => {
    const threshold = [
      { term: 'eq', value: 'A', color: '#ff0000ff' },
      { term: 'not_eq', value: 'B', color: '#00ff00ff' }
    ]
    const wrapper = mountComponent(threshold)
    const vm = wrapper.vm as any

    vm.removeThreshold(0)

    expect(vm.state.thresholdArr).toHaveLength(1)
    expect(vm.state.thresholdArr[0].term).toBe('not_eq')
  })

  it('emits onTextLabelThresholdChange with the current array', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.changeThreshold()

    expect(wrapper.emitted('onTextLabelThresholdChange')).toEqual([[vm.state.thresholdArr]])
  })

  it('does not mutate the original prop when adding entries', () => {
    const threshold = [{ term: 'eq', value: 'X' }]
    const wrapper = mountComponent(threshold)
    const vm = wrapper.vm as any

    vm.addThreshold()

    expect(threshold).toHaveLength(1)
  })
})
