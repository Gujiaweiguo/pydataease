import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

import DatasetDetail from '../DatasetDetail.vue'

describe('DatasetDetail', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(DatasetDetail, {
      props: { creator: 'admin', createTime: '2024-01-01' }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('displays creator prop', () => {
    const wrapper = shallowMount(DatasetDetail, {
      props: { creator: 'John', createTime: '2024-01-01' }
    })
    expect(wrapper.text()).toContain('John')
  })

  it('displays createTime prop', () => {
    const wrapper = shallowMount(DatasetDetail, {
      props: { creator: 'admin', createTime: '2024-06-15' }
    })
    expect(wrapper.text()).toContain('2024-06-15')
  })

  it('renders with default empty props', () => {
    const wrapper = shallowMount(DatasetDetail)
    expect(wrapper.exists()).toBe(true)
  })
})
