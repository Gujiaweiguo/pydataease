import { nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => `t:${key}`
  })
}))

import SecondAndMinute from '../cron/src/SecondAndMinute.vue'
import { ElCheckboxStub, ElInputNumberStub, cronStubs, lastEmission } from './testUtils/cronStubs'

const mountComponent = (props?: Record<string, unknown>) =>
  mount(SecondAndMinute, {
    props: {
      modelValue: '*',
      label: '秒',
      ...props
    },
    global: {
      stubs: cronStubs
    }
  })

describe('SecondAndMinute', () => {
  it('renders translated labels and all second checkboxes', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('t:cron.every秒')
    expect(wrapper.findAllComponents(ElCheckboxStub)).toHaveLength(60)
  })

  it('parses cycle expressions into the active radio and inputs', () => {
    const wrapper = mountComponent({ modelValue: '5-20' })
    const inputs = wrapper.findAllComponents(ElInputNumberStub)

    expect(wrapper.get('.el-radio-stub[data-label="2"]').attributes('data-checked')).toBe('true')
    expect(inputs[0].props('modelValue')).toBe('5')
    expect(inputs[1].props('modelValue')).toBe('20')
  })

  it('emits loop expressions after the repeat inputs change', async () => {
    const wrapper = mountComponent()
    const inputs = wrapper.findAllComponents(ElInputNumberStub)

    inputs[2].vm.$emit('update:modelValue', 5)
    inputs[2].vm.$emit('change', 5)
    inputs[3].vm.$emit('update:modelValue', 10)
    inputs[3].vm.$emit('change', 10)
    await nextTick()

    expect(lastEmission(wrapper)).toBe('5/10')
  })
})
