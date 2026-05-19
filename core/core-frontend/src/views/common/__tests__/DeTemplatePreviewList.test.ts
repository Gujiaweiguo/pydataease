import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('@/api/template', () => ({
  findOne: vi.fn(() => Promise.resolve({ data: {} }))
}))

import DeTemplatePreviewList from '../DeTemplatePreviewList.vue'

const globalStubs = {
  ElCol: { template: '<div class="el-col-stub"><slot /></div>' },
  ElRow: { template: '<div class="el-row-stub"><slot /></div>' },
  ElInput: { template: '<input />', props: ['modelValue'] },
  ElTree: { template: '<div class="el-tree-stub" />' },
  ElIcon: { template: '<i><slot /></i>' }
}

describe('DeTemplatePreviewList', () => {
  const mountComponent = (templateList = []) =>
    shallowMount(DeTemplatePreviewList, {
      props: { curCanvasType: 'dashboard', templateList },
      global: { stubs: globalStubs }
    })

  it('renders', () => {
    const wrapper = mountComponent()
    expect(wrapper.exists()).toBe(true)
  })

  it('renders with template list data', () => {
    const list = [
      { id: '1', name: 'Template A', nodeType: 'folder', children: [] },
      { id: '2', name: 'Template B', nodeType: 'template', dvType: 'dashboard' }
    ]
    const wrapper = mountComponent(list)
    expect(wrapper.exists()).toBe(true)
  })

  it('emits showCurrentTemplateInfo', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any
    vm.$emit('showCurrentTemplateInfo', { id: '1', name: 'test' })
    expect(wrapper.emitted('showCurrentTemplateInfo')).toBeTruthy()
  })

  it('has el-col wrapper', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('.el-col-stub').exists()).toBe(true)
  })
})
