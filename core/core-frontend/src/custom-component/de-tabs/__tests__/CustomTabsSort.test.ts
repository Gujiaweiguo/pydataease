import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: (store: Record<string, unknown>) => store
}))
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: vi.fn() })
}))
vi.mock('@/utils/utils', () => ({
  deepCopy: (obj: any) => JSON.parse(JSON.stringify(obj))
}))
vi.mock('@/utils/eventBus', () => ({
  default: { emit: vi.fn() }
}))
vi.mock('@/assets/svg/drag.svg', () => ({ default: 'mocked-drag-svg' }))

import CustomTabsSort from '../CustomTabsSort.vue'

const globalStubs = {
  'el-dialog': {
    template: '<div class="el-dialog"><slot /><slot name="footer" /></div>',
    props: ['modelValue', 'title', 'width', 'top', 'destroyOnClose', 'appendToBody']
  },
  'el-button': {
    template: '<button><slot /></button>',
    props: ['type']
  },
  'el-icon': {
    template: '<i><slot /></i>',
    props: ['size']
  },
  Icon: {
    template: '<span><slot /></span>',
    props: ['name']
  },
  draggable: {
    template: '<div class="draggable"><slot /></div>',
    props: ['list', 'animation']
  }
}

describe('de-tabs/CustomTabsSort.vue', () => {
  it('renders the component', () => {
    const wrapper = shallowMount(CustomTabsSort, { global: { stubs: globalStubs } })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders a dialog element', () => {
    const wrapper = shallowMount(CustomTabsSort, { global: { stubs: globalStubs } })
    expect(wrapper.find('.el-dialog').exists()).toBe(true)
  })

  it('exposes sortInit method', () => {
    const wrapper = shallowMount(CustomTabsSort, { global: { stubs: globalStubs } })
    expect(typeof (wrapper.vm as any).sortInit).toBe('function')
  })

  it('contains draggable component', () => {
    const wrapper = shallowMount(CustomTabsSort, { global: { stubs: globalStubs } })
    expect(wrapper.find('.draggable').exists()).toBe(true)
  })

  it('sortInit sets dialogShow to true', async () => {
    const wrapper = shallowMount(CustomTabsSort, { global: { stubs: globalStubs } })
    const component = {
      propValue: [{ name: 'tab1', title: 'Tab 1' }],
      id: 'test-id'
    }
    ;(wrapper.vm as any).sortInit(component)
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).dialogShow).toBe(true)
  })
})
