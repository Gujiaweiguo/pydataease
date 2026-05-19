import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/utils/imgUtils', () => ({
  imgUrlTrans: (url: string) => url
}))

import PictureItem from '../PictureItem.vue'

const stubs = {}

const mountPictureItem = (propsOverrides: Record<string, any> = {}) =>
  shallowMount(PictureItem, {
    props: {
      urlInfo: { url: 'https://example.com/image.jpg', name: 'test-image.jpg' },
      active: false,
      ...propsOverrides
    },
    global: { stubs }
  })

describe('PictureItem', () => {
  it('renders successfully with default props', () => {
    const wrapper = mountPictureItem()
    expect(wrapper.exists()).toBe(true)
  })

  it('renders an img element with the correct src', () => {
    const wrapper = mountPictureItem()
    const img = wrapper.find('img')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toBe('https://example.com/image.jpg')
  })

  it('displays the name text', () => {
    const wrapper = mountPictureItem()
    expect(wrapper.find('.name-area').text()).toBe('test-image.jpg')
  })

  it('applies selected-active class when active is true', () => {
    const wrapper = mountPictureItem({ active: true })
    expect(wrapper.find('.selected-active').exists()).toBe(true)
  })

  it('does not apply selected-active class when active is false', () => {
    const wrapper = mountPictureItem({ active: false })
    expect(wrapper.find('.selected-active').exists()).toBe(false)
  })
})
