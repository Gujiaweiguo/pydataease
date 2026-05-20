import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))

import Panel from '../index.vue'

describe('Panel', () => {
  it('renders component', () => {
    const wrapper = shallowMount(Panel)
    expect(wrapper.exists()).toBe(true)
  })

  it('displays panel text', () => {
    const wrapper = shallowMount(Panel)
    expect(wrapper.text()).toContain('panel')
  })
})
