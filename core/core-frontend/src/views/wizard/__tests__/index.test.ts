import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))

import Wizard from '../index.vue'

describe('Wizard', () => {
  it('renders component', () => {
    const wrapper = shallowMount(Wizard)
    expect(wrapper.exists()).toBe(true)
  })

  it('displays wizard text', () => {
    const wrapper = shallowMount(Wizard)
    expect(wrapper.text()).toContain('wizard')
  })
})
