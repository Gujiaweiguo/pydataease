import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

vi.mock('vuedraggable', () => ({
  default: { template: '<div><slot name="item" /><slot name="footer" /></div>', props: ['list', 'group', 'itemKey'] }
}))

import FilterHead from '@/views/visualized/view/panel/filter-config/FilterHead.vue'

const stubs = {
  draggable: { template: '<div><slot name="item" /><slot name="footer" /></div>', props: ['list', 'group', 'itemKey'] },
  ElTag: { template: '<span><slot /></span>', props: ['closable'] }
}

describe('FilterHead', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders successfully with empty drag items', () => {
    const wrapper = shallowMount(FilterHead, {
      props: { dragItems: [] },
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders with drag items', () => {
    const dragItems = [{ id: '1', name: 'Field 1' }, { id: '2', name: 'Field 2' }]
    const wrapper = shallowMount(FilterHead, {
      props: { dragItems },
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('has filter-header class', () => {
    const wrapper = shallowMount(FilterHead, {
      props: { dragItems: [] },
      global: { stubs }
    })
    expect(wrapper.find('.filter-header').exists()).toBe(true)
  })
})
