import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

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
    dvInfo: {
      id: '123',
      name: 'Test Dashboard',
      type: 'dataV',
      status: 1,
      weight: 9,
      ext: 0,
      creatorName: 'admin'
    }
  })
}))

vi.mock('@/store/modules/app', () => ({
  useAppStoreWithOut: () => ({
    getIsDataEaseBi: false,
    getIsIframe: false
  })
}))

vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => ({
    baseUrl: '',
    clearState: vi.fn(),
    setDvId: vi.fn(),
    setResourceId: vi.fn()
  })
}))

vi.mock('@/store/modules/share', () => ({
  useShareStoreWithOut: () => ({
    getShareDisable: false
  })
}))

vi.mock('@/api/visualization/dataVisualization', () => ({
  storeApi: vi.fn(() => Promise.resolve()),
  storeStatusApi: vi.fn(() => Promise.resolve({ data: false }))
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: vi.fn(() => ({
    emitter: { emit: vi.fn() }
  }))
}))

vi.mock('@/utils/utils', () => ({
  exportPermission: vi.fn(() => [true, false])
}))

vi.mock('@/utils/ModelUtil', () => ({
  isDesktop: vi.fn(() => false)
}))

vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div />' }
}))

vi.mock('vue-clipboard3', () => ({
  default: vi.fn(() => ({ copy: vi.fn() }))
}))

vi.mock('pinia', async importOriginal => {
  const actual = (await importOriginal()) as Record<string, unknown>
  return {
    ...actual,
    storeToRefs: vi.fn(() => ({
      dvInfo: {
        value: {
          id: '123',
          name: 'Test Dashboard',
          type: 'dataV',
          status: 1,
          weight: 9,
          ext: 0,
          creatorName: 'admin'
        }
      }
    }))
  }
})

import PreviewHead from '../PreviewHead.vue'

const globalStubs = {
  ElButton: { template: '<button><slot /><slot name="icon" /></button>' },
  ElTooltip: { template: '<div><slot /></div>' },
  ElIcon: { template: '<i><slot /></i>' },
  ElDivider: { template: '<div class="divider" />' },
  ElPopover: { template: '<div><slot /><slot name="reference" /></div>' },
  ElDropdown: { template: '<div><slot /><slot name="dropdown" /></div>' },
  ElDropdownMenu: { template: '<div><slot /></div>' },
  ElDropdownItem: { template: '<div><slot /></div>' },
  ShareVisualHead: {
    template: '<div />',
    props: ['disabled', 'resourceId', 'weight', 'resourceType']
  },
  DvDetailInfo: { template: '<div />' }
}

describe('PreviewHead', () => {
  const mountComponent = () =>
    shallowMount(PreviewHead, {
      global: { stubs: globalStubs }
    })

  it('renders', () => {
    const wrapper = mountComponent()
    expect(wrapper.exists()).toBe(true)
  })

  it('has preview-head class', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('.preview-head').exists()).toBe(true)
  })

  it('emits reload event', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any
    vm.$emit('reload', '123')
    const reloadEvents = wrapper.emitted('reload')
    expect(reloadEvents).toBeTruthy()
    expect(reloadEvents?.[0]).toEqual(['123'])
  })

  it('emits download event', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any
    vm.$emit('download', 'pdf')
    const downloadEvents = wrapper.emitted('download')
    expect(downloadEvents).toBeTruthy()
    expect(downloadEvents?.[0]).toEqual(['pdf'])
  })

  it('emits downloadAsAppTemplate event', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any
    vm.$emit('downloadAsAppTemplate', 'template')
    expect(wrapper.emitted('downloadAsAppTemplate')).toBeTruthy()
  })
})
