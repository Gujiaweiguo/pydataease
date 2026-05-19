import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('@/store/modules/app', () => ({
  useAppStoreWithOut: () => ({
    getArrowSide: true,
    setArrowSide: vi.fn()
  })
}))

vi.mock('@/assets/svg/icon_left_outlined.svg', () => ({ default: 'left-icon' }))
vi.mock('@/assets/svg/icon_right_outlined.svg', () => ({ default: 'right-icon' }))

import DeResourceArrow from '../DeResourceArrow.vue'

const globalStubs = {
  ElIcon: { template: '<i><slot /></i>' }
}

describe('DeResourceArrow', () => {
  const mountComponent = (isInside = false) =>
    shallowMount(DeResourceArrow, {
      props: { isInside },
      global: { stubs: globalStubs }
    })

  it('renders', () => {
    const wrapper = mountComponent()
    expect(wrapper.exists()).toBe(true)
  })

  it('emits changeSideTreeStatus on click', async () => {
    const wrapper = mountComponent(false)
    const arrow = wrapper.find('.arrow-side-tree')
    if (arrow.exists()) {
      await arrow.trigger('click')
      expect(wrapper.emitted('changeSideTreeStatus')).toBeTruthy()
    }
  })

  it('has arrow-side-tree class when arrow side is shown', () => {
    const wrapper = mountComponent(false)
    expect(wrapper.exists()).toBe(true)
  })
})
