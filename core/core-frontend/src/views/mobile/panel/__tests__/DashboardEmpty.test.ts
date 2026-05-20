import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

import DashboardEmpty from '../DashboardEmpty.vue'

describe('DashboardEmpty', () => {
  it('renders component', () => {
    const wrapper = shallowMount(DashboardEmpty)
    expect(wrapper.exists()).toBe(true)
  })

  it('contains not-support div', () => {
    const wrapper = shallowMount(DashboardEmpty)
    expect(wrapper.find('.not-support').exists()).toBe(true)
  })

  it('displays mobile not enabled message', () => {
    const wrapper = shallowMount(DashboardEmpty)
    expect(wrapper.text()).toContain('仪表板未开启移动端')
  })
})
