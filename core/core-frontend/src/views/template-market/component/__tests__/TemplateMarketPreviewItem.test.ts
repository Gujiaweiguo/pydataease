import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/utils/imgUtils', () => ({
  imgUrlTrans: (url: string) => url
}))

import TemplateMarketPreviewItem from '../TemplateMarketPreviewItem.vue'

describe('TemplateMarketPreviewItem', () => {
  const template = {
    id: 'preview-1',
    title: 'Preview Template',
    thumbnail: 'http://example.com/preview.png'
  }

  it('renders without errors', () => {
    const wrapper = shallowMount(TemplateMarketPreviewItem, {
      props: { template, baseUrl: 'http://example.com/', active: false }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('displays template title', () => {
    const wrapper = shallowMount(TemplateMarketPreviewItem, {
      props: { template, baseUrl: 'http://example.com/', active: false }
    })
    expect(wrapper.find('.demonstration').text()).toBe('Preview Template')
  })

  it('applies active class when active prop is true', () => {
    const wrapper = shallowMount(TemplateMarketPreviewItem, {
      props: { template, baseUrl: 'http://example.com/', active: true }
    })
    expect(wrapper.find('.template-item-main-active').exists()).toBe(true)
  })

  it('does not apply active class when active prop is false', () => {
    const wrapper = shallowMount(TemplateMarketPreviewItem, {
      props: { template, baseUrl: 'http://example.com/', active: false }
    })
    expect(wrapper.find('.template-item-main-active').exists()).toBe(false)
  })

  it('emits previewTemplate on click', async () => {
    const wrapper = shallowMount(TemplateMarketPreviewItem, {
      props: { template, baseUrl: 'http://example.com/', active: false }
    })
    await wrapper.find('.template-item-main').trigger('click')
    const previewTemplateEvents = wrapper.emitted('previewTemplate')
    expect(previewTemplateEvents).toBeTruthy()
    expect(previewTemplateEvents?.[0]?.[0]).toEqual(template)
  })
})
