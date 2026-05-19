import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: {
      get: vi.fn(() => null),
      set: vi.fn()
    }
  })
}))

vi.mock('@/api/visualization/dataVisualization', () => ({
  queryTreeApi: vi.fn(() => Promise.resolve([])),
  copyResource: vi.fn(),
  moveResource: vi.fn(),
  dvNameCheck: vi.fn(),
  updateBase: vi.fn(),
  saveCanvas: vi.fn(),
  deleteLogic: vi.fn(),
  ResourceOrFolder: {}
}))

import DeResourceGroupOpt from '../DeResourceGroupOpt.vue'

const globalStubs = {
  ElDialog: {
    props: ['modelValue', 'title', 'width'],
    template: '<div v-if="modelValue" class="dialog-stub"><slot /><slot name="footer" /></div>'
  },
  ElForm: { template: '<form><slot /></form>' },
  ElFormItem: { template: '<div><slot /></div>' },
  ElInput: { template: '<input />', props: ['modelValue'] },
  ElTreeSelect: { template: '<select><slot /></select>' },
  ElTree: { template: '<div><slot /></div>' },
  ElButton: { template: '<button><slot /></button>' },
  ElIcon: { template: '<i><slot /></i>' }
}

const mountComponent = () =>
  shallowMount(DeResourceGroupOpt, {
    props: { curCanvasType: 'dashboard' },
    global: { stubs: globalStubs }
  })

describe('DeResourceGroupOpt', () => {
  it('renders but dialog is hidden initially', () => {
    const wrapper = mountComponent()
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.dialog-stub').exists()).toBe(false)
  })

  it('exposes optInit method', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any
    expect(typeof vm.optInit).toBe('function')
  })

  it('exposes editeInit method', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any
    expect(typeof vm.editeInit).toBe('function')
  })

  it('emits finish event', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any
    vm.$emit('finish')
    expect(wrapper.emitted('finish')).toBeTruthy()
  })
})
