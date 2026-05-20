import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/api/visualization/dataVisualization', () => ({
  queryTreeApi: vi.fn(() => Promise.resolve([]))
}))

vi.mock('@/utils/canvasUtils', () => ({
  filterEmptyFolderTree: vi.fn((list: any) => list)
}))

vi.mock('@/assets/svg/dv-dashboard-spine.svg', () => ({}))
vi.mock('@/assets/svg/dv-folder.svg', () => ({}))

import SelectScreenDialog from '../SelectScreenDialog.vue'

const mountComponent = () =>
  shallowMount(SelectScreenDialog, {
    global: {
      mocks: { $t: (key: string) => key },
      stubs: {
        'el-dialog': { template: '<div class="el-dialog"><slot /><slot name="footer" /></div>' },
        'el-button': { template: '<button><slot /></button>' },
        'el-form-item': { template: '<div><slot /></div>' },
        'el-tree-select': { template: '<div class="el-tree-select" />' },
        'el-icon': { template: '<i><slot /></i>' }
      }
    }
  })

describe('de-screen/SelectScreenDialog', () => {
  it('renders the dialog container', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('.el-dialog').exists()).toBe(true)
  })

  it('exposes init method', () => {
    const wrapper = mountComponent()
    expect(typeof (wrapper.vm as any).init).toBe('function')
  })

  it('init sets dialogVisible to true', async () => {
    const wrapper = mountComponent()
    ;(wrapper.vm as any).init({ dvType: 'dashboard', screenId: null })
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).dialogVisible).toBe(true)
  })

  it('emits selectConfirm on confirm', async () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any
    vm.confirm()
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('selectConfirm')).toBeTruthy()
  })
})
