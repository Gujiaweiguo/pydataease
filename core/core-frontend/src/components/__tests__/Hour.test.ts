import { nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => `t:${key}`
  })
}))

import Hour from '../cron/src/Hour.vue'
import { ElCheckboxStub, ElInputNumberStub, cronStubs, lastEmission } from './testUtils/cronStubs'

const mountComponent = (props?: Record<string, unknown>) =>
  mount(Hour, {
    props: {
      modelValue: '*',
      ...props
    },
    global: {
      stubs: cronStubs
    }
  })

describe('Hour', () => {
  it('renders the hourly options and 24 selectable checkboxes', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('t:cron.every_hour')
    expect(wrapper.findAllComponents(ElCheckboxStub)).toHaveLength(24)
  })

  it('parses loop expressions into the repeat controls', () => {
    const wrapper = mountComponent({ modelValue: '3/6' })
    const inputs = wrapper.findAllComponents(ElInputNumberStub)

    expect(wrapper.get('.el-radio-stub[data-label="3"]').attributes('data-checked')).toBe('true')
    expect(inputs[2].props('modelValue')).toBe('3')
    expect(inputs[3].props('modelValue')).toBe('6')
  })

  it('emits selected hours after the checkbox mode becomes active', async () => {
    const wrapper = mountComponent()
    const checkboxGroup = wrapper.getComponent({ name: 'ElCheckboxGroup' })

    checkboxGroup.vm.$emit('update:modelValue', ['1', '12', '23'])
    wrapper.findAllComponents(ElCheckboxStub)[0].vm.$emit('change', '1')
    await nextTick()

    expect(lastEmission(wrapper)).toBe('1,12,23')
  })
})
