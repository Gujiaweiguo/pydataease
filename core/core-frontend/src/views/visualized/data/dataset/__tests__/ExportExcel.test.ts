import { defineComponent } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.stubGlobal('import.meta', { env: { VITE_API_BASEPATH: '/api' } })

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('@/config/axios/service', () => ({
  PATH_URL: '/api'
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: vi.fn()
}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({ wsCache: { get: vi.fn() } })
}))

vi.mock('@/api/dataset', () => ({
  exportTasks: vi.fn(),
  exportRetry: vi.fn(),
  exportDelete: vi.fn(),
  exportDeleteAll: vi.fn(),
  exportDeletePost: vi.fn(),
  exportTasksRecords: vi.fn(),
  generateDownloadUri: vi.fn()
}))

vi.mock('@/api/font', () => ({
  edit: vi.fn()
}))

vi.mock('@/store/modules/link', () => ({
  useLinkStoreWithOut: () => ({ getLinkToken: false })
}))

vi.mock('@/store/modules/app', () => ({
  useAppStoreWithOut: () => ({ getIsDataEaseBi: false, getIsIframe: false })
}))

import ExportExcel from '../ExportExcel.vue'

const globalStubs = {
  ElDrawer: defineComponent({
    name: 'ElDrawer',
    props: ['modelValue'],
    template: '<div v-if="modelValue" class="el-drawer-stub"><slot /><slot name="footer" /></div>'
  }),
  ElTabs: { template: '<div><slot /></div>' },
  ElTabPane: { template: '<div><slot /></div>' },
  ElButton: { template: '<button><slot /></button>' },
  ElTable: { template: '<table><slot /></table>' },
  ElTableColumn: { template: '<col />' },
  ElTooltip: { template: '<div><slot /></div>' },
  ElDialog: defineComponent({
    name: 'ElDialog',
    props: ['modelValue'],
    template: '<div v-if="modelValue"><slot /><slot name="footer" /></div>'
  }),
  ElIcon: { template: '<i><slot /></i>' },
  ElProgress: { template: '<div class="progress" />' },
  Icon: { template: '<span><slot /></span>' },
  GridTable: { template: '<div class="grid-table-stub"><slot /></div>' },
  EmptyBackground: { template: '<div class="empty-bg-stub" />' }
}

describe('ExportExcel', () => {
  const mountOpts = { global: { stubs: globalStubs, mocks: { $t: (k: string) => k }, directives: { loading: () => undefined } } }

  it('renders without errors', () => {
    const wrapper = shallowMount(ExportExcel, mountOpts)
    expect(wrapper.exists()).toBe(true)
  })

  it('exposes init method', () => {
    const wrapper = shallowMount(ExportExcel, mountOpts)
    expect(typeof (wrapper.vm as any).init).toBe('function')
  })

  it('drawer is closed by default', () => {
    const wrapper = shallowMount(ExportExcel, mountOpts)
    expect(wrapper.find('.el-drawer-stub').exists()).toBe(false)
  })

  it('has timestampFormatDate utility', () => {
    const wrapper = shallowMount(ExportExcel, mountOpts)
    expect(typeof (wrapper.vm as any).timestampFormatDate).toBe('function')
  })
})
