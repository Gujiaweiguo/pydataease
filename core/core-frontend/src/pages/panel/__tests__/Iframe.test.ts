import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => ({
    outerUrl: 'https://example.com',
    setType: vi.fn(),
    setBusiFlag: vi.fn(),
    setOuterParams: vi.fn(),
    setSuffixId: vi.fn(),
    setToken: vi.fn(),
    setBaseUrl: vi.fn(),
    setDvId: vi.fn(),
    setPid: vi.fn(),
    setResourceId: vi.fn(),
    setDfId: vi.fn()
  })
}))

import Iframe from '../Iframe.vue'

describe('panel/Iframe.vue', () => {
  it('renders the component', () => {
    const wrapper = shallowMount(Iframe)
    expect(wrapper.exists()).toBe(true)
  })

  it('contains an iframe element', () => {
    const wrapper = shallowMount(Iframe)
    expect(wrapper.find('iframe').exists()).toBe(true)
  })

  it('iframe has correct src from computed outerUrl', () => {
    const wrapper = shallowMount(Iframe)
    const iframe = wrapper.find('iframe')
    expect(iframe.attributes('src')).toBe('https://example.com')
  })

  it('iframe has frameborder="0"', () => {
    const wrapper = shallowMount(Iframe)
    const iframe = wrapper.find('iframe')
    expect(iframe.attributes('frameborder')).toBe('0')
  })

  it('has de-jump_outer_url class', () => {
    const wrapper = shallowMount(Iframe)
    expect(wrapper.find('iframe').classes()).toContain('de-jump_outer_url')
  })
})
