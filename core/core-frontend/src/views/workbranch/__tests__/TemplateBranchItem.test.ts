import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/utils/imgUtils', () => ({
  imgUrlTrans: (url: string) => url
}))

vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div />' }
}))

import TemplateBranchItem from '../TemplateBranchItem.vue'

const globalStubs = {
  ElButton: { template: '<button><slot /></button>' },
  ElIcon: { template: '<i><slot /></i>' },
  ElTooltip: { template: '<div><slot /></div>' }
}

const defaultTemplate = {
  id: 'tpl-1',
  title: 'My Template',
  thumbnail: 'http://example.com/thumb.png',
  templateType: 'PANEL'
}

const mountItem = (props = {}) =>
  shallowMount(TemplateBranchItem, {
    props: {
      template: defaultTemplate,
      createAuth: { PANEL: true, SCREEN: true },
      baseUrl: 'http://cdn.example.com/',
      ...props
    },
    global: { stubs: globalStubs }
  })

describe('TemplateBranchItem', () => {
  it('renders the template title', () => {
    const wrapper = mountItem()
    expect(wrapper.text()).toContain('My Template')
  })

  it('computes classBackground with thumbnail URL', () => {
    const wrapper = mountItem()
    const imgDiv = wrapper.find('.img')
    expect(imgDiv.exists()).toBe(true)
    const style = imgDiv.attributes('style')
    expect(style).toContain('http://example.com/thumb.png')
  })

  it('emits templateApply when apply method is called', () => {
    const wrapper = mountItem()
    const vm = wrapper.vm as any
    vm.apply()
    expect(wrapper.emitted('templateApply')).toBeTruthy()
    expect(wrapper.emitted('templateApply')?.[0]).toEqual([defaultTemplate])
  })

  it('emits templatePreview when templateInnerPreview method is called', () => {
    const wrapper = mountItem()
    const vm = wrapper.vm as any
    vm.templateInnerPreview()
    expect(wrapper.emitted('templatePreview')).toBeTruthy()
    expect(wrapper.emitted('templatePreview')?.[0]).toEqual(['tpl-1'])
  })
})
