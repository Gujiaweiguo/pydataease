import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/utils/imgUtils', () => ({
  imgUrlTrans: (url: string) => url
}))

import TemplateMarketItem from '../TemplateMarketItem.vue'

const globalStubs = {
  ElRow: { template: '<div><slot /></div>' },
  ElButton: { template: '<button><slot /></button>', props: ['size', 'style', 'type'] }
}

describe('TemplateMarketItem', () => {
  const template = {
    id: 'tmpl-1',
    title: 'My Template',
    thumbnail: 'http://example.com/thumb.png'
  }

  it('renders without errors', () => {
    const wrapper = shallowMount(TemplateMarketItem, {
      props: { template, baseUrl: 'http://example.com/', width: 200 },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('displays template title', () => {
    const wrapper = shallowMount(TemplateMarketItem, {
      props: { template, baseUrl: 'http://example.com/', width: 200 },
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.demonstration').text()).toBe('My Template')
  })

  it('emits templateApply when apply button is clicked', async () => {
    const wrapper = shallowMount(TemplateMarketItem, {
      props: { template, baseUrl: 'http://example.com/', width: 200 },
      global: { stubs: globalStubs }
    })
    await wrapper.vm.$nextTick()
    const vm = wrapper.vm as any
    vm.apply()
    const templateApplyEvents = wrapper.emitted('templateApply')
    expect(templateApplyEvents).toBeTruthy()
    expect(templateApplyEvents?.[0]?.[0]).toEqual(template)
  })

  it('emits templatePreview when preview is triggered', async () => {
    const wrapper = shallowMount(TemplateMarketItem, {
      props: { template, baseUrl: 'http://example.com/', width: 200 },
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    vm.templateInnerPreview()
    const templatePreviewEvents = wrapper.emitted('templatePreview')
    expect(templatePreviewEvents).toBeTruthy()
    expect(templatePreviewEvents?.[0]?.[0]).toBe('tmpl-1')
  })

  it('computes classBackground with width-based dimensions', () => {
    const wrapper = shallowMount(TemplateMarketItem, {
      props: { template, baseUrl: 'http://example.com/', width: 300 },
      global: { stubs: globalStubs }
    })
    const imgEl = wrapper.find('.template-img')
    expect(imgEl.exists()).toBe(true)
  })
})
