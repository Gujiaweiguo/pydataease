import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/utils/propTypes', () => ({
  propTypes: {
    string: { def: (v: string) => v },
    bool: { def: (v: boolean) => v }
  }
}))

vi.mock('element-plus-secondary', () => ({
  ElMessage: { error: vi.fn() }
}))

vi.mock('./SecondAndMinute.vue', () => ({
  default: { template: '<div class="second-and-minute-stub" />' }
}))

vi.mock('./Hour.vue', () => ({
  default: { template: '<div class="hour-stub" />' }
}))

vi.mock('./Day.vue', () => ({
  default: { template: '<div class="day-stub" />' }
}))

vi.mock('./Month.vue', () => ({
  default: { template: '<div class="month-stub" />' }
}))

vi.mock('./Week.vue', () => ({
  default: { template: '<div class="week-stub" />' }
}))

vi.mock('./Year.vue', () => ({
  default: { template: '<div class="year-stub" />' }
}))

import Cron from '../Cron.vue'

const mountComponent = (props = {}) =>
  shallowMount(Cron, {
    props: {
      modelValue: '* * * * * ? *',
      isRate: false,
      ...props
    },
    global: {
      stubs: {
        'el-tabs': { template: '<div class="el-tabs"><slot /></div>' },
        'el-tab-pane': { template: '<div class="el-tab-pane"><slot /></div>' },
        'el-table': { template: '<div class="el-table"><slot /></div>' },
        'el-table-column': { template: '<div class="el-table-column" />' }
      }
    }
  })

describe('cron/Cron', () => {
  it('renders the root container', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('div').exists()).toBe(true)
  })

  it('accepts modelValue prop', () => {
    const wrapper = mountComponent({ modelValue: '0 0 * * * ? *' })
    expect(wrapper.props('modelValue')).toBe('0 0 * * * ? *')
  })

  it('accepts isRate prop default false', () => {
    const wrapper = mountComponent()
    expect(wrapper.props('isRate')).toBe(false)
  })

  it('initializes state with activeName s', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any
    expect(vm.state.activeName).toBe('s')
  })

  it('parses modelValue into separate fields', () => {
    const wrapper = mountComponent({ modelValue: '0 30 12 * * ? 2025' })
    const vm = wrapper.vm as any
    expect(vm.state.sVal).toBe('0')
    expect(vm.state.mVal).toBe('30')
    expect(vm.state.hVal).toBe('12')
    expect(vm.state.yearVal).toBe('2025')
  })
})
