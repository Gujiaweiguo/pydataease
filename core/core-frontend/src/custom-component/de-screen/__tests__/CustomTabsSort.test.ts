import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: vi.fn()
  })
}))

vi.mock('@/utils/utils', () => ({
  deepCopy: (obj: any) => JSON.parse(JSON.stringify(obj))
}))

vi.mock('@/utils/eventBus', () => ({
  default: { on: vi.fn(), off: vi.fn(), emit: vi.fn() }
}))

vi.mock('vuedraggable', () => ({
  default: { template: '<div class="draggable-stub"><slot /></div>' }
}))

vi.mock('@/assets/svg/drag.svg', () => ({}))

vi.mock('element-plus-secondary', () => ({
  ElButton: { template: '<button><slot /></button>' }
}))

import CustomTabsSort from '../CustomTabsSort.vue'

const mountComponent = () =>
  shallowMount(CustomTabsSort, {
    global: {
      mocks: { $t: (key: string) => key },
      stubs: {
        'el-dialog': { template: '<div class="el-dialog"><slot /><slot name="footer" /></div>' },
        'el-button': { template: '<button><slot /></button>' },
        'el-icon': { template: '<i><slot /></i>' }
      }
    }
  })

describe('de-screen/CustomTabsSort', () => {
  it('renders the root container', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('.el-dialog').exists()).toBe(true)
  })

  it('exposes sortInit method', () => {
    const wrapper = mountComponent()
    expect(typeof (wrapper.vm as any).sortInit).toBe('function')
  })

  it('sortInit sets dialogShow to true', async () => {
    const wrapper = mountComponent()
    const component = {
      id: 'test-comp',
      propValue: [
        { name: 'tab1', title: 'Tab 1' },
        { name: 'tab2', title: 'Tab 2' }
      ]
    }
    ;(wrapper.vm as any).sortInit(component)
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).dialogShow).toBe(true)
  })
})
