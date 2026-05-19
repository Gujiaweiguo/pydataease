import { defineComponent } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({ wsCache: { get: vi.fn() } })
}))

vi.mock('@/api/dataset', () => ({
  getDatasetTree: vi.fn(),
  moveDatasetTree: vi.fn(),
  createDatasetTree: vi.fn(),
  renameDatasetTree: vi.fn()
}))

vi.mock('element-plus-secondary', () => ({
  ElMessage: { success: vi.fn(), error: vi.fn() }
}))

import CreatDsGroup from '../CreatDsGroup.vue'

const globalStubs = {
  ElButton: { template: '<button><slot /></button>' },
  ElDialog: defineComponent({
    name: 'ElDialog',
    props: ['modelValue', 'title', 'width'],
    template: '<div v-if="modelValue" class="el-dialog-stub"><slot /><slot name="footer" /></div>'
  }),
  ElInput: { template: '<input />', props: ['modelValue'] },
  ElForm: { template: '<form><slot /></form>' },
  ElFormItem: { template: '<div><slot /></div>' },
  ElTreeSelect: { template: '<select><slot /></select>' },
  ElTree: { template: '<div><slot /></div>' },
  ElIcon: { template: '<i><slot /></i>' },
  Icon: { template: '<span><slot /></span>' }
}

describe('CreatDsGroup', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(CreatDsGroup, { global: { stubs: globalStubs } })
    expect(wrapper.exists()).toBe(true)
  })

  it('exposes createInit method', () => {
    const wrapper = shallowMount(CreatDsGroup, { global: { stubs: globalStubs } })
    expect(typeof (wrapper.vm as any).createInit).toBe('function')
  })

  it('exposes editeInit method', () => {
    const wrapper = shallowMount(CreatDsGroup, { global: { stubs: globalStubs } })
    expect(typeof (wrapper.vm as any).editeInit).toBe('function')
  })

  it('dialog is hidden by default', () => {
    const wrapper = shallowMount(CreatDsGroup, { global: { stubs: globalStubs } })
    expect(wrapper.find('.el-dialog-stub').exists()).toBe(false)
  })
})
