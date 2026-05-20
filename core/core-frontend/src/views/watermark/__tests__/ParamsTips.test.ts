import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))

import ParamsTips from '../ParamsTips.vue'

describe('ParamsTips', () => {
  const stubs = {
    ElTooltip: {
      template: '<div><slot /><slot name="content" /></div>',
      props: ['effect', 'placement']
    },
    ElIcon: { template: '<i><slot /></i>' }
  }

  it('renders component', () => {
    const wrapper = shallowMount(ParamsTips, {
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('has tips-class wrapper', () => {
    const wrapper = shallowMount(ParamsTips, {
      global: { stubs }
    })
    expect(wrapper.find('.tips-class').exists()).toBe(true)
  })
})
