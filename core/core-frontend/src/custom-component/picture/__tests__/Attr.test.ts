import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

const { mockCurComponent } = vi.hoisted(() => ({
  mockCurComponent: { propValue: { url: '' }, style: { adaptation: 'adaptation' } }
}))

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: vi.fn(), resetStyleChangeTimes: vi.fn() })
}))
vi.mock('@/api/staticResource', () => ({ beforeUploadCheck: vi.fn(), uploadFileResult: vi.fn() }))
vi.mock('@/utils/imgUtils', () => ({ imgUrlTrans: (url: string) => url }))
vi.mock('@/utils/eventBus', () => ({ default: { on: vi.fn(), off: vi.fn(), emit: vi.fn() } }))
vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({ curComponent: mockCurComponent, mobileInPc: false })
}))
import { ref } from 'vue'
vi.mock('pinia', async (importOriginal) => {
  const actual = await importOriginal() as any
  return { ...actual, storeToRefs: () => ({ curComponent: ref(mockCurComponent), mobileInPc: ref(false) }) }
})

import Attr from '../Attr.vue'

const stubs = {
  CommonAttr: { template: '<div class="common-attr"><slot /></div>',
    props: ['themes', 'element', 'backgroundColorPickerWidth', 'backgroundBorderSelectWidth'] },
  'el-collapse-item': { template: '<div class="el-collapse-item"><slot /></div>', props: ['effect', 'title', 'name'] },
  'el-row': { template: '<div class="el-row"><slot /></div>' },
  'el-col': { template: '<div class="el-col"><slot /></div>', props: ['style'] },
  'el-upload': { template: '<div class="el-upload"><slot /></div>', props: ['action', 'accept', 'listType', 'fileList'] },
  'el-icon': { template: '<span><slot /></span>' },
  'el-button': { template: '<button><slot /></button>', props: ['size', 'text'] },
  'el-form-item': { template: '<div class="el-form-item"><slot /></div>', props: ['label', 'size', 'effect', 'class'] },
  'el-radio-group': { template: '<div><slot /></div>', props: ['modelValue', 'size', 'effect'] },
  'el-radio': { template: '<label><slot /></label>', props: ['value', 'effect'] },
  ImgViewDialog: { template: '<div class="img-view-dialog" />', props: ['modelValue', 'imageUrl'] },
  Plus: { template: '<span>+</span>' }
}

const mountAttr = (propsOverrides: Record<string, any> = {}) =>
  shallowMount(Attr, { props: { themes: 'dark', ...propsOverrides }, global: { stubs } })

describe('picture/Attr', () => {
  it('renders successfully with default props', () => { expect(mountAttr().exists()).toBe(true) })
  it('renders the attr-list container', () => { expect(mountAttr().find('.attr-list').exists()).toBe(true) })
  it('renders CommonAttr component', () => { expect(mountAttr().find('.common-attr').exists()).toBe(true) })
  it('passes themes prop to CommonAttr', () => { expect(mountAttr({ themes: 'light' }).find('.common-attr').exists()).toBe(true) })
})
