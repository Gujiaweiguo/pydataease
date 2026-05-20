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
  storeToRefs: vi.fn(() => ({ canvasStyleData: { value: { themeId: 'default' } } })),
  createPinia: vi.fn()
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    canvasStyleData: { themeId: 'default' },
    setCanvasStyle: vi.fn()
  })
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: vi.fn() })
}))

vi.mock('@/utils/imgUtils', () => ({
  imgUrlTrans: (url: string) => url
}))

vi.mock('@/utils/canvasStyle', () => ({
  adaptCurThemeCommonStyleAll: vi.fn()
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({ emitter: { emit: vi.fn() } })
}))

vi.mock('@/assets/svg/dv-no-img.svg', () => ({ default: { template: '<svg />' } }))

vi.mock('element-plus-secondary', () => ({
  ElMessageBox: { confirm: vi.fn(() => Promise.resolve()) },
  ElTooltip: { template: '<div><slot /></div>', props: ['effect', 'placement', 'content'] }
}))

import SubjectTemplateItem from '@/components/dashboard/subject-setting/pre-subject/SubjectTemplateItem.vue'

const stubs = {
  Icon: { template: '<span><slot /></span>', props: ['name'] },
  ElTooltip: { template: '<div><slot /></div>', props: ['effect', 'placement', 'content'] },
  ElButton: { template: '<button><slot /></button>', props: ['text', 'class', 'style'] },
  ElIcon: { template: '<i><slot /></i>', props: ['size'] },
  Delete: { template: '<svg />' },
  EditPen: { template: '<svg />' },
  dvNoImg: { template: '<svg />', props: ['class', 'style'] }
}

describe('SubjectTemplateItem', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders successfully', () => {
    const subjectItem = {
      id: '1',
      name: 'Test Theme',
      coverUrl: '',
      details: '{"themeId":"default"}',
      type: 'system'
    }
    const wrapper = shallowMount(SubjectTemplateItem, {
      props: { subjectItem },
      global: { stubs, mocks: { $t: (k: string) => k } }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders with self type', () => {
    const subjectItem = {
      id: '2',
      name: 'My Theme',
      coverUrl: '',
      details: '{"themeId":"custom"}',
      type: 'self'
    }
    const wrapper = shallowMount(SubjectTemplateItem, {
      props: { subjectItem },
      global: { stubs, mocks: { $t: (k: string) => k } }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('has subject-template class', () => {
    const subjectItem = {
      id: '1',
      name: 'Test',
      coverUrl: '',
      details: '{"themeId":"default"}',
      type: 'system'
    }
    const wrapper = shallowMount(SubjectTemplateItem, {
      props: { subjectItem },
      global: { stubs, mocks: { $t: (k: string) => k } }
    })
    expect(wrapper.find('.subject-template').exists()).toBe(true)
  })
})
