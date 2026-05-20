import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/assets/svg/401.svg', () => ({ default: '' }))
vi.mock('@/components/icon-custom', () => ({
  Icon: { template: '<div><slot /></div>' }
}))

import Error401 from '../index.vue'

describe('Error401', () => {
  it('renders component', () => {
    const wrapper = shallowMount(Error401, {
      global: {
        stubs: { Icon: { template: '<div><slot /></div>' } }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('has page-not-found class', () => {
    const wrapper = shallowMount(Error401, {
      global: {
        stubs: { Icon: { template: '<div><slot /></div>' } }
      }
    })
    expect(wrapper.find('.page-not-found').exists()).toBe(true)
  })
})
