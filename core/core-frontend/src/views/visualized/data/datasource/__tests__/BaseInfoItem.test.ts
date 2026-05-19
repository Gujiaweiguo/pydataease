import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

import BaseInfoItem from '../BaseInfoItem.vue'

describe('BaseInfoItem', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(BaseInfoItem, {
      props: { label: 'Host' }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('displays the label prop', () => {
    const wrapper = shallowMount(BaseInfoItem, {
      props: { label: 'Host' }
    })
    expect(wrapper.text()).toContain('Host')
  })

  it('renders slot content as the value', () => {
    const wrapper = shallowMount(BaseInfoItem, {
      props: { label: 'Port' },
      slots: { default: '5432' }
    })
    expect(wrapper.text()).toContain('5432')
  })

  it('renders with empty label default', () => {
    const wrapper = shallowMount(BaseInfoItem)
    expect(wrapper.exists()).toBe(true)
  })
})
