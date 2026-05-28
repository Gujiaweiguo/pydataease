import { nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => `t:${key}`
  })
}))

import Day from '../cron/src/Day.vue'
import { ElCheckboxStub, ElInputNumberStub, cronStubs, lastEmission } from './testUtils/cronStubs'

const mountComponent = (props?: Record<string, unknown>) =>
  mount(Day, {
    props: {
      modelValue: '?',
      ...props
    },
    global: {
      stubs: cronStubs
    }
  })

describe('Day', () => {
  it('renders the day presets and 31 explicit day checkboxes', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('t:cron.work_day')
    expect(wrapper.findAllComponents(ElCheckboxStub)).toHaveLength(31)
  })

  it('parses workday expressions into the dedicated radio and input', () => {
    const wrapper = mountComponent({ modelValue: '15W' })
    const inputs = wrapper.findAllComponents(ElInputNumberStub)

    expect(wrapper.get('.el-radio-stub[data-label="8"]').attributes('data-checked')).toBe('true')
    expect(inputs[4].props('modelValue')).toBe(15)
  })

  it('emits cycle expressions when the range inputs change', async () => {
    const wrapper = mountComponent()
    const inputs = wrapper.findAllComponents(ElInputNumberStub)

    inputs[0].vm.$emit('update:modelValue', 2)
    inputs[0].vm.$emit('change', 2)
    inputs[1].vm.$emit('update:modelValue', 10)
    inputs[1].vm.$emit('change', 10)
    await nextTick()

    expect(lastEmission(wrapper)).toBe('2-10')
  })
})
