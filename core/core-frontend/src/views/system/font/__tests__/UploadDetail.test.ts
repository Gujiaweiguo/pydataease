import { defineComponent } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('@/api/font', () => ({
  uploadFontFile: vi.fn(),
  edit: vi.fn()
}))

vi.mock('element-plus-secondary', () => ({
  ElMessage: { success: vi.fn(), error: vi.fn() }
}))

import UploadDetail from '../UploadDetail.vue'

const globalStubs = {
  ElDialog: defineComponent({
    name: 'ElDialog',
    props: ['modelValue', 'title'],
    template: '<div v-if="modelValue"><slot /><slot name="footer" /></div>'
  }),
  ElForm: { template: '<form><slot /></form>' },
  ElFormItem: { template: '<div><slot /></div>' },
  ElInput: { template: '<input />', props: ['modelValue'] },
  ElUpload: { template: '<div><slot name="trigger" /></div>' },
  ElButton: { template: '<button><slot /></button>' },
  FontInfo: { template: '<div class="font-info-stub" />' },
  Icon: { template: '<span><slot /></span>' }
}

describe('UploadDetail', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(UploadDetail, { global: { stubs: globalStubs } })
    expect(wrapper.exists()).toBe(true)
  })

  it('exposes init method', () => {
    const wrapper = shallowMount(UploadDetail, { global: { stubs: globalStubs } })
    expect(typeof (wrapper.vm as any).init).toBe('function')
  })

  it('dialog is hidden by default', () => {
    const wrapper = shallowMount(UploadDetail, { global: { stubs: globalStubs } })
    expect(wrapper.find('.el-dialog-stub').exists()).toBe(false)
  })

  it('has beforeAvatarUpload that rejects non-ttf files', () => {
    const wrapper = shallowMount(UploadDetail, { global: { stubs: globalStubs } })
    const result = (wrapper.vm as any).beforeAvatarUpload({ name: 'test.txt' })
    expect(result).toBe(false)
  })
})
