import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('tinymce/tinymce', () => {
  const mock = {
    init: vi.fn(),
    editors: {},
    activeEditor: { selection: { getNode: vi.fn() } },
    get: vi.fn()
  }
  return { default: mock, __esModule: true }
})
vi.mock('@tinymce/tinymce-vue', () => ({
  default: {
    name: 'Editor',
    template: '<div class="tinymce-editor-stub" />',
    props: ['modelValue', 'init', 'disabled', 'id']
  }
}))
vi.mock('tinymce/themes/silver/theme', () => ({}))
vi.mock('tinymce/icons/default', () => ({}))
vi.mock('tinymce/plugins/advlist', () => ({}))
vi.mock('tinymce/plugins/autolink', () => ({}))
vi.mock('tinymce/plugins/link', () => ({}))
vi.mock('tinymce/plugins/image', () => ({}))
vi.mock('tinymce/plugins/lists', () => ({}))
vi.mock('tinymce/plugins/charmap', () => ({}))
vi.mock('tinymce/plugins/media', () => ({}))
vi.mock('tinymce/plugins/wordcount', () => ({}))
vi.mock('tinymce/plugins/table', () => ({}))
vi.mock('tinymce/plugins/contextmenu', () => ({}))
vi.mock('tinymce/plugins/directionality', () => ({}))
vi.mock('tinymce/plugins/nonbreaking', () => ({}))
vi.mock('tinymce/plugins/pagebreak', () => ({}))
vi.mock('@npkg/tinymce-plugins/letterspacing', () => ({}))
vi.mock('../plugins', () => ({}))
vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: vi.fn(), resetStyleChangeTimes: vi.fn() })
}))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    dvInfo: { type: 'dashboard' },
    canvasViewInfo: {},
    mobileInPc: false,
    setViewDataDetails: vi.fn()
  })
}))
vi.mock('@/store/modules/appearance', () => ({
  useAppearanceStoreWithOut: () => ({ fontList: [], setCurrentFont: vi.fn() })
}))
vi.mock('@/store/modules/user', () => ({ useUserStoreWithOut: () => ({ getLanguage: 'zh-CN' }) }))
vi.mock('@/utils/url', () => ({ formatDataEaseBi: (url: string) => url }))
vi.mock('@/utils/eventBus', () => ({ default: { on: vi.fn(), off: vi.fn(), emit: vi.fn() } }))
vi.mock('@/api/chart', () => ({
  getData: () => Promise.resolve({ data: { fields: [], tableRow: [], sourceFields: [] } })
}))
vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({ emitter: { emit: vi.fn(), on: vi.fn() } })
}))
vi.mock('pinia', async importOriginal => {
  const actual = (await importOriginal()) as any
  return {
    ...actual,
    storeToRefs: () => ({ canvasViewInfo: { value: {} }, mobileInPc: { value: false } })
  }
})

import DeRichTextView from '../DeRichTextView.vue'

const stubs = {
  Editor: {
    template: '<div class="editor-stub" />',
    props: ['modelValue', 'init', 'disabled', 'id']
  },
  'chart-error': { template: '<div class="chart-error" />', props: ['errMsg'] }
}

const createElement = {
  id: 'rich-text-1',
  propValue: { textValue: '<p>Hello</p>', verticalAlign: 'top-align' },
  style: {},
  canvasId: 'canvas-main'
}

const mountRichText = (propsOverrides: Record<string, any> = {}) =>
  shallowMount(DeRichTextView, {
    props: {
      scale: 1,
      element: createElement,
      editMode: 'edit',
      active: false,
      disabled: false,
      showPosition: 'preview',
      themes: 'dark',
      suffixId: 'common',
      ...propsOverrides
    },
    global: { stubs }
  })

describe('DeRichTextView', () => {
  it('renders successfully with default props', () => {
    expect(mountRichText().exists()).toBe(true)
  })
  it('renders the rich-main-class container', () => {
    expect(mountRichText().find('.rich-main-class').exists()).toBe(true)
  })
  it('does not have edit-model class initially', () => {
    expect(mountRichText().find('.edit-model').exists()).toBe(false)
  })
  it('exposes calcData and renderChart methods', () => {
    const vm = mountRichText().vm as any
    expect(typeof vm.calcData).toBe('function')
    expect(typeof vm.renderChart).toBe('function')
  })
  it('does not render chart-error when isError is false', () => {
    expect(mountRichText().find('.chart-error').exists()).toBe(false)
  })
})
