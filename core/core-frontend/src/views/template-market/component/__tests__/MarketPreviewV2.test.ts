import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/utils/imgUtils', () => ({
  imgUrlTrans: (url: string) => url
}))

vi.mock('@/utils/utils', () => ({
  deepCopy: (val: any) => JSON.parse(JSON.stringify(val)),
  getActiveCategories: () => new Set(['Recommended'])
}))

vi.mock('@/api/templateMarket', () => ({
  searchMarketPreview: vi.fn(() =>
    Promise.resolve({
      data: {
        baseUrl: 'https://dataease.io/templates',
        contents: [],
        categories: []
      }
    })
  )
}))

import MarketPreviewV2 from '../MarketPreviewV2.vue'

const globalStubs = {
  ElRow: { template: '<div><slot /></div>' },
  ElCol: { template: '<div><slot /></div>' },
  ElTooltip: { template: '<div><slot /></div>' },
  ElIcon: { template: '<i><slot /></i>' },
  ElInput: {
    template: '<input />',
    props: ['modelValue', 'prefixIcon', 'placeholder', 'clearable']
  },
  ElSelect: { template: '<select><slot /></select>', props: ['modelValue', 'placeholder'] },
  ElOption: { template: '<option />', props: ['label', 'value', 'key'] },
  ElButton: { template: '<button><slot /></button>', props: ['type', 'disabled', 'style'] },
  ElDivider: { template: '<hr />' },
  ElMain: { template: '<main><slot /></main>' },
  ElCollapse: { template: '<div><slot /></div>', props: ['modelValue'] },
  ElCollapseItem: {
    template: '<div><slot /><slot name="title" /></div>',
    props: ['name', 'key', 'title', 'themes']
  },
  TemplateMarketPreviewItem: { template: '<div />', props: ['template', 'baseUrl', 'active'] },
  Icon: { template: '<i><slot /></i>' },
  ArrowRight: { template: '<span>→</span>' }
}

describe('MarketPreviewV2', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(MarketPreviewV2, {
      props: { previewId: null, templateShowList: [], createAuth: { PANEL: false, SCREEN: false } },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('emits closePreview when closePreview is called', () => {
    const wrapper = shallowMount(MarketPreviewV2, {
      props: { previewId: null, templateShowList: [], createAuth: { PANEL: false, SCREEN: false } },
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    vm.closePreview()
    expect(wrapper.emitted('closePreview')).toBeTruthy()
  })

  it('initial state has asideActive as true', () => {
    const wrapper = shallowMount(MarketPreviewV2, {
      props: { previewId: null, templateShowList: [], createAuth: { PANEL: false, SCREEN: false } },
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.state.asideActive).toBe(true)
  })

  it('toggles asideActive via asideActiveChange', () => {
    const wrapper = shallowMount(MarketPreviewV2, {
      props: { previewId: null, templateShowList: [], createAuth: { PANEL: false, SCREEN: false } },
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    vm.asideActiveChange(false)
    expect(vm.state.asideActive).toBe(false)
  })

  it('has default createAuth values', () => {
    const wrapper = shallowMount(MarketPreviewV2, {
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.state.templateTypeOptions.length).toBe(3)
  })

  it('emits templateApply when templateApply is called', () => {
    const wrapper = shallowMount(MarketPreviewV2, {
      props: { previewId: null, templateShowList: [], createAuth: { PANEL: false, SCREEN: false } },
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    const tpl = { id: '1', title: 'Test' }
    vm.templateApply(tpl)
    const templateApplyEvents = wrapper.emitted('templateApply')
    expect(templateApplyEvents).toBeTruthy()
    expect(templateApplyEvents?.[0]?.[0]).toEqual(tpl)
  })

  it('state has correct default baseUrl', () => {
    const wrapper = shallowMount(MarketPreviewV2, {
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.state.baseUrl).toBe('https://dataease.io/templates')
  })
})
