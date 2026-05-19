import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: {
      get: vi.fn(() => 280),
      set: vi.fn()
    }
  })
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: vi.fn(() => undefined)
}))

vi.mock('@/assets/svg/icon_side-fold_outlined.svg', () => ({ default: 'fold-icon' }))
vi.mock('@/assets/svg/icon_side-expand_outlined.svg', () => ({ default: 'expand-icon' }))

import CollapseBar from '../CollapseBar.vue'

const globalStubs = {
  ElIcon: { template: '<i><slot /></i>' }
}

describe('CollapseBar', () => {
  const mountComponent = (isCollapse = false) =>
    shallowMount(CollapseBar, {
      props: { isCollapse },
      global: {
        stubs: globalStubs,
        mocks: {
          $t: (k: string) => k
        }
      }
    })

  it('renders', () => {
    const wrapper = mountComponent()
    expect(wrapper.exists()).toBe(true)
  })

  it('has collapse bar class', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('.de-collapse-bar').exists()).toBe(true)
  })

  it('emits setCollapse on click', async () => {
    const wrapper = mountComponent(false)
    await wrapper.find('.de-collapse-bar').trigger('click')
    expect(wrapper.emitted('setCollapse')).toBeTruthy()
    expect(wrapper.emitted('setCollapse')![0]).toEqual([true])
  })

  it('emits setCollapse true when collapsed', async () => {
    const wrapper = mountComponent(true)
    await wrapper.find('.de-collapse-bar').trigger('click')
    expect(wrapper.emitted('setCollapse')).toBeTruthy()
    expect(wrapper.emitted('setCollapse')![0]).toEqual([false])
  })
})
