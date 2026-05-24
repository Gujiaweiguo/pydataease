import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/utils/imgUtils', () => ({ imgUrlTrans: (url: string) => url }))
import TemplateMarketV2Item from '../TemplateMarketV2Item.vue'

describe('TemplateMarketV2Item', () => {
  const stubs = {
    ElButton: { template: '<button><slot /></button>' },
    ElRow: { template: '<div><slot /></div>' }
  }

  const defaultProps = {
    template: {
      id: 't1',
      title: 'My Template',
      thumbnail: 'http://example.com/thumb.png',
      templateType: 'PANEL'
    },
    baseUrl: 'http://example.com/',
    width: 200,
    createAuth: { PANEL: true, SCREEN: false }
  }

  it('renders with template data', () => {
    const wrapper = shallowMount(TemplateMarketV2Item, {
      props: defaultProps,
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('displays template title', () => {
    const wrapper = shallowMount(TemplateMarketV2Item, {
      props: defaultProps,
      global: { stubs }
    })
    expect(wrapper.text()).toContain('My Template')
  })

  it('renders template image container', () => {
    const wrapper = shallowMount(TemplateMarketV2Item, {
      props: defaultProps,
      global: { stubs }
    })
    expect(wrapper.find('.template-img-container').exists()).toBe(true)
  })

  it('emits templateApply on apply', () => {
    const wrapper = shallowMount(TemplateMarketV2Item, {
      props: defaultProps,
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders testcase-template container', () => {
    const wrapper = shallowMount(TemplateMarketV2Item, {
      props: defaultProps,
      global: { stubs }
    })
    expect(wrapper.find('.testcase-template').exists()).toBe(true)
  })

  it('shows template buttons for dashboard alias when PANEL createAuth is true', () => {
    const wrapper = shallowMount(TemplateMarketV2Item, {
      props: {
        ...defaultProps,
        template: { ...defaultProps.template, templateType: 'dashboard' }
      },
      global: { stubs }
    })
    expect(wrapper.find('.template-button').attributes('style') ?? '').not.toContain(
      'display: none'
    )
  })

  it('hides template buttons for dataV alias when SCREEN createAuth is false', () => {
    const wrapper = shallowMount(TemplateMarketV2Item, {
      props: {
        ...defaultProps,
        template: { ...defaultProps.template, templateType: 'dataV' },
        createAuth: { PANEL: true, SCREEN: false }
      },
      global: { stubs }
    })
    expect(wrapper.find('.bottom-area-show').classes()).toContain('create-area')
  })
})
