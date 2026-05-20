import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (k: string) => k
  })
}))
vi.mock('@/assets/svg/icon_left_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_close_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_delete-trash_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_right_outlined.svg', () => ({ default: '' }))
vi.mock('@/components/icon-custom', () => ({
  Icon: { template: '<span><slot /></span>' }
}))

import FilterText from '../FilterText.vue'

describe('FilterText', () => {
  const globalStubs = {
    'el-divider': true,
    'el-icon': true,
    'el-tooltip': true,
    'el-button': { template: '<button><slot /><slot name="icon" /></button>', props: ['type'] }
  }

  it('should not render when filterTexts is empty', () => {
    const wrapper = shallowMount(FilterText, {
      props: { filterTexts: [], total: 0 },
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.filter-texts').exists()).toBe(false)
  })

  it('should render when filterTexts has items', () => {
    const wrapper = shallowMount(FilterText, {
      props: { filterTexts: ['filter1'], total: 1 },
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.filter-texts').exists()).toBe(true)
  })
})
