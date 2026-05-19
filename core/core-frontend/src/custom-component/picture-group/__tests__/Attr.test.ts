import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

const { mockCurComponent } = vi.hoisted(() => ({
  mockCurComponent: { id: 'pg-1', innerType: 'picture-group', propValue: { url: '' }, style: {} }
}))

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/store/modules/data-visualization/snapshot', () => ({ snapshotStoreWithOut: () => ({ recordSnapshotCacheToMobile: vi.fn() }) }))
vi.mock('@/config/axios/service', () => ({ service: {} as any, PATH_URL: './', cancelMap: new Map() }))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({ curComponent: mockCurComponent, canvasViewInfo: {}, mobileInPc: false, batchOptStatus: false })
}))
import { ref } from 'vue'
vi.mock('pinia', async (importOriginal) => {
  const actual = await importOriginal() as any
  return { ...actual, storeToRefs: () => ({
    curComponent: ref(mockCurComponent), canvasViewInfo: ref({}), mobileInPc: ref(false), batchOptStatus: ref(false)
  })}
})

import Attr from '../Attr.vue'

const stubs = {
  CommonAttr: { template: '<div class="common-attr"><slot /><slot name="carousel" /><slot name="threshold" /></div>',
    props: ['themes', 'element', 'backgroundColorPickerWidth', 'backgroundBorderSelectWidth'] },
  'picture-group-upload-attr': { template: '<div class="pg-upload" />', props: ['themes', 'element', 'view'] },
  'picture-group-dataset-select': { template: '<div class="pg-dataset" />', props: ['themes', 'view'] },
  'carousel-setting': { template: '<div class="carousel-setting" />', props: ['element', 'themes'] },
  'picture-group-threshold': { template: '<div class="pg-threshold"><slot name="dataset" /></div>', props: ['themes', 'element', 'view'] }
}

const mountAttr = (propsOverrides: Record<string, any> = {}) =>
  shallowMount(Attr, { props: { themes: 'dark', ...propsOverrides }, global: { stubs } })

describe('picture-group/Attr', () => {
  it('renders successfully with default props', () => { expect(mountAttr().exists()).toBe(true) })
  it('renders the attr-list container', () => { expect(mountAttr().find('.attr-list').exists()).toBe(true) })
  it('renders CommonAttr component', () => { expect(mountAttr().find('.common-attr').exists()).toBe(true) })
  it('passes themes prop correctly', () => { expect(mountAttr({ themes: 'light' }).find('.common-attr').exists()).toBe(true) })
})
