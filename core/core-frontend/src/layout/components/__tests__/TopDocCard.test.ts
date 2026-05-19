import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: {
      get: vi.fn(() => null),
      set: vi.fn()
    }
  })
}))

import TopDocCard from '../TopDocCard.vue'

const globalStubs = {
  ElIcon: { template: '<i><slot /></i>' }
}

describe('TopDocCard', () => {
  const defaultCardInfo = { name: 'Docs', url: 'https://example.com', icon: 'doc-icon' }

  const mountComponent = (cardInfo = defaultCardInfo) =>
    shallowMount(TopDocCard, {
      props: { cardInfo },
      global: { stubs: globalStubs }
    })

  it('renders', () => {
    const wrapper = mountComponent()
    expect(wrapper.exists()).toBe(true)
  })

  it('displays card name', () => {
    const wrapper = mountComponent({ name: 'Help Center', url: 'https://help.com', icon: 'help-icon' })
    expect(wrapper.text()).toContain('Help Center')
  })

  it('has doc-card class', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('.doc-card').exists()).toBe(true)
  })

  it('handles default empty card info', () => {
    const wrapper = shallowMount(TopDocCard, {
      props: {
        cardInfo: { name: '', url: '', icon: '' }
      },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('calls window.open on click when url is set', async () => {
    const openSpy = vi.spyOn(window, 'open').mockImplementation(() => undefined)
    const wrapper = mountComponent()
    await wrapper.find('.doc-card').trigger('click')
    expect(openSpy).toHaveBeenCalled()
    openSpy.mockRestore()
  })
})
