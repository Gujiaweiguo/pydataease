import { nextTick } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (key: string) => key }) }))
vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div />' },
  loadPlugin: () => undefined
}))
vi.mock('@/config/axios/hmac', () => ({}))

import TimeDialog from '../TimeDialog.vue'

const globalStubs = {
  DynamicTime: {
    props: ['config'],
    template:
      '<div class="dynamic-time-stub" :data-granularity="config.timeGranularity" :data-relative="config.relativeToCurrent" />'
  },
  ElForm: { template: '<form class="form-stub"><slot /></form>' },
  ElFormItem: {
    props: ['label'],
    template: '<div class="form-item-stub" :data-label="label"><slot /></div>'
  },
  ElSelect: { props: ['modelValue'], template: '<select class="select-stub"><slot /></select>' },
  ElOption: {
    props: ['label', 'value'],
    template: '<option class="option-stub" :value="value">{{ label }}</option>'
  },
  ElInputNumber: {
    props: ['modelValue'],
    template: '<input class="input-number-stub" type="number" />'
  },
  ElTimePicker: {
    props: ['modelValue'],
    template: '<input class="time-picker-stub" type="time" />'
  }
}

const mountComponent = () =>
  shallowMount(TimeDialog, {
    global: {
      stubs: globalStubs
    }
  })

describe('TimeDialog', () => {
  it('starts with the default year-based selection config', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    expect(vm.curComponent.timeGranularity).toBe('year')
    expect(vm.curComponent.relativeToCurrent).toBe('custom')
    expect(wrapper.get('.dynamic-time-stub').attributes('data-granularity')).toBe('year')
  })

  it('init merges incoming values onto the default selection config', async () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.init({ timeGranularity: 'date', relativeToCurrent: 'today', timeNum: 2 })
    await nextTick()

    expect(vm.curComponent.timeGranularity).toBe('date')
    expect(vm.curComponent.relativeToCurrent).toBe('today')
    expect(vm.relativeToCurrentList.map(item => item.value)).toContain('monthBeginning')
  })

  it('resets custom relative type and picks the first preset when granularity changes', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.curComponent.timeGranularity = 'date'
    vm.curComponent.relativeToCurrent = 'today'
    vm.curComponent.relativeToCurrentType = 'date'
    vm.timeGranularityChange('month')

    expect(vm.curComponent.relativeToCurrentType).toBe('year')
    expect(vm.curComponent.relativeToCurrent).toBe('thisMonth')
  })

  it('shows the time picker for custom datetime selections', async () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.init({ timeGranularity: 'datetime', relativeToCurrent: 'custom' })
    await nextTick()

    expect(wrapper.find('.time-picker-stub').exists()).toBe(true)
  })
})
