import { nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => `t:${key}`
  })
}))

import Month from '../cron/src/Month.vue'
import { ElCheckboxStub, ElInputNumberStub, cronStubs, lastEmission } from './testUtils/cronStubs'

const mountComponent = (props?: Record<string, unknown>) =>
  mount(Month, {
    props: {
      modelValue: '*',
      ...props
    },
    global: {
      stubs: cronStubs
    }
  })

describe('Month', () => {
  it('renders all month checkboxes and the monthly presets', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('t:cron.every_month')
    expect(wrapper.findAllComponents(ElCheckboxStub)).toHaveLength(12)
  })

  it('parses not-set expressions into the corresponding radio option', () => {
    const wrapper = mountComponent({ modelValue: '?' })

    expect(wrapper.get('.el-radio-stub[data-label="5"]').attributes('data-checked')).toBe('true')
  })

  it('emits repeat expressions from the looping inputs', async () => {
    const wrapper = mountComponent()
    const inputs = wrapper.findAllComponents(ElInputNumberStub)

    inputs[2].vm.$emit('update:modelValue', 3)
    inputs[2].vm.$emit('change', 3)
    inputs[3].vm.$emit('update:modelValue', 2)
    inputs[3].vm.$emit('change', 2)
    await nextTick()

    expect(lastEmission(wrapper)).toBe('3/2')
  })
})
