import { nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => `t:${key}`
  })
}))

import Year from '../cron/src/Year.vue'
import { ElInputNumberStub, cronStubs, lastEmission } from './testUtils/cronStubs'

const mountComponent = (props?: Record<string, unknown>) =>
  mount(Year, {
    props: {
      modelValue: '*',
      ...props
    },
    global: {
      stubs: cronStubs
    }
  })

describe('Year', () => {
  it('renders yearly presets and cycle inputs', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('t:cron.every_year')
    expect(wrapper.findAllComponents(ElInputNumberStub)).toHaveLength(2)
  })

  it('parses range expressions into the year inputs', () => {
    const wrapper = mountComponent({ modelValue: '2024-2028' })
    const inputs = wrapper.findAllComponents(ElInputNumberStub)

    expect(wrapper.get('.el-radio-stub[data-label="2"]').attributes('data-checked')).toBe('true')
    expect(inputs[0].props('modelValue')).toBe('2024')
    expect(inputs[1].props('modelValue')).toBe('2028')
  })

  it('emits wildcard expressions when every-year mode is selected', async () => {
    const wrapper = mountComponent({ modelValue: '2024-2028' })

    await wrapper.get('.el-radio-stub[data-label="1"]').trigger('click')
    await nextTick()

    expect(lastEmission(wrapper)).toBe('*')
  })
})
