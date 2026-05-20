import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/store', () => ({ store: {} }))

vi.mock('pinia', () => ({
  defineStore: vi.fn(),
  storeToRefs: vi.fn(() => ({})),
  createPinia: vi.fn()
}))

vi.mock('@/utils/utils', () => ({
  deepCopy: (v: any) => JSON.parse(JSON.stringify(v))
}))

vi.mock('@/components/visualization/common/DeUpload.vue', () => ({
  default: { template: '<div><slot /></div>', props: ['themes', 'imgUrl'] }
}))

import SubjectEditDialog from '@/components/dashboard/subject-setting/pre-subject/SubjectEditDialog.vue'

const stubs = {
  ElDialog: {
    template: '<div v-if="modelValue"><slot /><slot name="footer" /></div>',
    props: ['title', 'modelValue', 'width']
  },
  ElForm: {
    template: '<form><slot /></form>',
    props: ['labelPosition', 'requireAsteriskPosition', 'model', 'rules']
  },
  ElFormItem: { template: '<div><slot /><slot name="label" /></div>', props: ['class', 'prop'] },
  ElInput: { template: '<input />', props: ['modelValue'] },
  ElButton: { template: '<button><slot /></button>', props: ['secondary', 'type'] },
  DeUpload: { template: '<div />', props: ['themes', 'imgUrl'] }
}

describe('SubjectEditDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders successfully', () => {
    const wrapper = shallowMount(SubjectEditDialog, {
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('exposes optInit method', () => {
    const wrapper = shallowMount(SubjectEditDialog, {
      global: { stubs }
    })
    expect(typeof (wrapper.vm as any).optInit).toBe('function')
  })

  it('exposes resetForm method', () => {
    const wrapper = shallowMount(SubjectEditDialog, {
      global: { stubs }
    })
    expect(typeof (wrapper.vm as any).resetForm).toBe('function')
  })
})
