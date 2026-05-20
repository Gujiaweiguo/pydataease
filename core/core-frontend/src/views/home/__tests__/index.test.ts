import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))

import Home from '../index.vue'

describe('Home', () => {
  it('renders component', () => {
    const wrapper = shallowMount(Home, {
      global: {
        stubs: { ElDatePicker: { template: '<input />' } }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains a div wrapper', () => {
    const wrapper = shallowMount(Home, {
      global: {
        stubs: { ElDatePicker: { template: '<input />' } }
      }
    })
    expect(wrapper.find('div').exists()).toBe(true)
  })
})
