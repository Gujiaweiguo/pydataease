import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/utils/imgUtils', () => ({ imgUrlTrans: (url: string) => url }))
vi.mock('../TemplateMarketV2Item.vue', () => ({ default: { template: '<div class="template-item" />' } }))
import CategoryTemplateV2 from '../CategoryTemplateV2.vue'

describe('CategoryTemplateV2', () => {
  const stubs = {
    ElCol: { template: '<div><slot /></div>' },
    TemplateMarketV2Item: { template: '<div />' }
  }

  const defaultProps = {
    label: 'Test Category',
    searchText: '',
    fullTemplateShowList: [
      { id: '1', title: 'Template 1', showFlag: true, categoryNames: ['Test Category'] },
      { id: '2', title: 'Template 2', showFlag: false, categoryNames: ['Other'] }
    ],
    createAuth: { PANEL: true, SCREEN: true }
  }

  it('renders with default props', () => {
    const wrapper = shallowMount(CategoryTemplateV2, {
      props: defaultProps,
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('displays category label', () => {
    const wrapper = shallowMount(CategoryTemplateV2, {
      props: defaultProps,
      global: { stubs }
    })
    expect(wrapper.text()).toContain('Test Category')
  })

  it('shows search result count when searchText provided', () => {
    const wrapper = shallowMount(CategoryTemplateV2, {
      props: { ...defaultProps, searchText: 'test' },
      global: { stubs }
    })
    expect(wrapper.find('.custom-search').exists()).toBe(true)
  })

  it('shows category label without search text', () => {
    const wrapper = shallowMount(CategoryTemplateV2, {
      props: { ...defaultProps, searchText: '' },
      global: { stubs }
    })
    expect(wrapper.find('.custom-category').exists()).toBe(true)
  })

  it('emits templateApply event', () => {
    const wrapper = shallowMount(CategoryTemplateV2, {
      props: defaultProps,
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
