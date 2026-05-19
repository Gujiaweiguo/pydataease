import { nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => `t:${key}`
  })
}))

import Week from '../cron/src/Week.vue'
import { ElCheckboxStub, ElInputNumberStub, cronStubs, lastEmission } from './testUtils/cronStubs'

const mountComponent = (props?: Record<string, unknown>) =>
  mount(Week, {
    props: {
      modelValue: '*',
      ...props
    },
    global: {
      stubs: cronStubs
    }
  })

describe('Week', () => {
  it('renders the weekly tip text and seven checkbox options', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('t:cron.week_tips')
    expect(wrapper.findAllComponents(ElCheckboxStub)).toHaveLength(7)
  })

  it('parses cycle expressions into the week range inputs', () => {
    const wrapper = mountComponent({ modelValue: '2-6' })
    const inputs = wrapper.findAllComponents(ElInputNumberStub)

    expect(wrapper.get('.el-radio-stub[data-label="2"]').attributes('data-checked')).toBe('true')
    expect(inputs[0].props('modelValue')).toBe('2')
    expect(inputs[1].props('modelValue')).toBe('6')
  })

  it('emits repeat expressions when weekly repeat values change', async () => {
    const wrapper = mountComponent()
    const inputs = wrapper.findAllComponents(ElInputNumberStub)

    inputs[2].vm.$emit('update:modelValue', 2)
    inputs[2].vm.$emit('change', 2)
    inputs[3].vm.$emit('update:modelValue', 3)
    inputs[3].vm.$emit('change', 3)
    await nextTick()

    expect(lastEmission(wrapper)).toBe('2/3')
  })
})
