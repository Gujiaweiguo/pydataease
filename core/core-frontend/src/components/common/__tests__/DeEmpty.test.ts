import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (k: string) => k
  })
}))
vi.mock('../../empty-background/src/EmptyBackground.vue', () => ({
  default: { template: '<div class="empty-bg-stub"><slot /></div>' }
}))

import DeEmpty from '../DeEmpty.vue'

describe('DeEmpty', () => {
  it('should render without errors', () => {
    const wrapper = shallowMount(DeEmpty, {
      global: {
        stubs: {
          'el-row': { template: '<div class="el-row-stub"><slot /></div>' }
        }
      }
    })
    expect(wrapper.find('.custom-position').exists()).toBe(true)
  })
})
