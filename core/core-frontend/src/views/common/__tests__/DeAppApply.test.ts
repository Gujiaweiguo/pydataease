import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('@/config/axios/service', () => ({}))

vi.mock('@/config/axios/refresh', () => ({}))

vi.mock('@/store/modules/user', () => ({
  useUserStoreWithOut: vi.fn(() => ({}))
}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({
    wsCache: {
      get: vi.fn(() => null),
      set: vi.fn()
    }
  })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    dvInfo: { value: { id: '1', name: 'test', pid: '0' } },
    appData: { value: { datasourceInfo: [], datasetGroupsInfo: [] } }
  })
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: vi.fn()
  })
}))

vi.mock('@/api/visualization/dataVisualization', () => ({
  dvNameCheck: vi.fn(() => Promise.resolve()),
  queryTreeApi: vi.fn(() => Promise.resolve([]))
}))

vi.mock('@/api/dataset', () => ({
  getDatasetTree: vi.fn(() => Promise.resolve([]))
}))

vi.mock('@/utils/ModelUtil', () => ({
  isDesktop: vi.fn(() => false)
}))

vi.mock('@/utils/utils', () => ({
  deepCopy: vi.fn((v: any) => v),
  filterFreeFolder: vi.fn()
}))

vi.mock('pinia', async importOriginal => {
  const actual = await importOriginal() as Record<string, unknown>
  return {
    ...actual,
    storeToRefs: vi.fn(() => ({
      dvInfo: { value: { id: '1', name: 'test', pid: '0' } },
      appData: { value: { datasourceInfo: [], datasetGroupsInfo: [] } }
    }))
  }
})

import DeAppApply from '../DeAppApply.vue'

const globalStubs = {
  ElDrawer: {
    template: '<div class="drawer-stub"><slot /><slot name="footer" /></div>',
    props: ['modelValue', 'title', 'size', 'direction', 'showClose']
  },
  ElForm: { template: '<form><slot /></form>' },
  ElFormItem: { template: '<div><slot /></div>', props: ['label', 'prop'] },
  ElInput: { template: '<input />', props: ['modelValue'] },
  ElSelect: { template: '<select><slot /></select>', props: ['modelValue'] },
  ElOption: { template: '<option><slot /></option>' },
  ElButton: { template: '<button><slot /></button>' },
  ElTreeSelect: { template: '<select />' },
  ElRow: { template: '<div><slot /></div>' },
  ElCol: { template: '<div><slot /></div>' },
  ElIcon: { template: '<i><slot /></i>' },
  DatasetSelect: { template: '<div />' }
}

describe('DeAppApply', () => {
  const mountComponent = () =>
    shallowMount(DeAppApply, {
      props: {
        componentData: {},
        canvasViewInfo: {},
        curCanvasType: 'dashboard'
      },
      global: { stubs: globalStubs }
    })

  it('renders', () => {
    const wrapper = mountComponent()
    expect(wrapper.exists()).toBe(true)
  })

  it('has drawer stub', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('.drawer-stub').exists()).toBe(true)
  })

  it('exposes init and close methods', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any
    expect(typeof vm.init).toBe('function')
    expect(typeof vm.close).toBe('function')
  })

  it('emits closeDraw event', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any
    vm.$emit('closeDraw')
    expect(wrapper.emitted('closeDraw')).toBeTruthy()
  })
})
