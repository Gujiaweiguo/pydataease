import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

import NotSupport from '../NotSupport.vue'

describe('NotSupport', () => {
  it('renders component', () => {
    const wrapper = shallowMount(NotSupport)
    expect(wrapper.exists()).toBe(true)
  })

  it('contains not-support div', () => {
    const wrapper = shallowMount(NotSupport)
    expect(wrapper.find('.not-support').exists()).toBe(true)
  })

  it('displays warning text', () => {
    const wrapper = shallowMount(NotSupport)
    expect(wrapper.text()).toContain('数据大屏不支持在移动端查阅')
  })
})
