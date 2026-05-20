import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))

import Auth from '../Auth.vue'

describe('Auth', () => {
  it('renders component', () => {
    const wrapper = shallowMount(Auth)
    expect(wrapper.exists()).toBe(true)
  })

  it('displays auth text', () => {
    const wrapper = shallowMount(Auth)
    expect(wrapper.text()).toContain('auth')
  })
})
