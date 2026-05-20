import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))

import Application from '../index.vue'

describe('Application', () => {
  it('renders component', () => {
    const wrapper = shallowMount(Application)
    expect(wrapper.exists()).toBe(true)
  })

  it('displays wizard text', () => {
    const wrapper = shallowMount(Application)
    expect(wrapper.text()).toContain('wizard')
  })
})
