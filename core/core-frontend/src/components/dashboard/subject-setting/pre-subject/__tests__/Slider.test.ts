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

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    canvasStyleData: { component: {} }
  })
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: vi.fn() })
}))

vi.mock('@/api/visualization/dataVisualization', () => ({
  querySubjectWithGroupApi: vi.fn(() => Promise.resolve({ data: [[{ id: '1', name: 'test', details: '{}' }]] })),
  saveOrUpdateSubject: vi.fn(() => Promise.resolve()),
  deleteSubject: vi.fn(() => Promise.resolve())
}))

vi.mock('@/utils/utils', () => ({
  deepCopy: (v: any) => JSON.parse(JSON.stringify(v))
}))

vi.mock('@/views/visualized/data/dataset/form/util.js', () => ({
  guid: () => 'test-guid'
}))

vi.mock('@/utils/eventBus', () => ({
  default: { on: vi.fn(), off: vi.fn(), emit: vi.fn() }
}))

vi.mock('element-plus-secondary', () => ({
  ElMessage: { success: vi.fn() }
}))

vi.mock('@/components/dashboard/subject-setting/pre-subject/SubjectTemplateItem.vue', () => ({
  default: { template: '<div />', props: ['subjectItem'] }
}))

vi.mock('@/components/dashboard/subject-setting/pre-subject/SubjectEditDialog.vue', () => ({
  default: { template: '<div />', expose: ['optInit', 'resetForm'] }
}))

import Slider from '@/components/dashboard/subject-setting/pre-subject/Slider.vue'

const stubs = {
  ElRow: { template: '<div><slot /></div>', props: ['style'] },
  ElCol: { template: '<div><slot /></div>', props: ['span'] },
  SubjectTemplateItem: { template: '<div />', props: ['subjectItem'] },
  SubjectEditDialog: { template: '<div />' }
}

describe('Slider', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders successfully', () => {
    const wrapper = shallowMount(Slider, { global: { stubs } })
    expect(wrapper.exists()).toBe(true)
  })

  it('exposes saveSelfSubject method', () => {
    const wrapper = shallowMount(Slider, { global: { stubs } })
    expect(typeof wrapper.vm.saveSelfSubject).toBe('function')
  })

  it('accepts initialSpeed and initialInterval props', () => {
    const wrapper = shallowMount(Slider, {
      props: { initialSpeed: 50, initialInterval: 5 },
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
