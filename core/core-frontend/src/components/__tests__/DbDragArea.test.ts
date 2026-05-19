import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const eventBusMock = vi.hoisted(() => ({
  emit: vi.fn()
}))

const dvMainStoreMock = vi.hoisted(() => ({
  setInEditorStatus: vi.fn(),
  setClickComponentStatus: vi.fn(),
  setCurComponent: vi.fn()
}))

vi.mock('@/utils/eventBus', () => ({
  default: eventBusMock
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => dvMainStoreMock
}))

import DbDragArea from '@/components/dashboard/DbDragArea.vue'

describe('DbDragArea', () => {
  const item = { id: 'component-1', component: 'VText' }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders four drag handles', () => {
    const wrapper = mount(DbDragArea, {
      props: { item, index: 2 }
    })

    expect(wrapper.findAll('.dragHandle')).toHaveLength(4)
  })

  it('updates editor store state on mouseup', async () => {
    const wrapper = mount(DbDragArea, {
      props: { item, index: 2 }
    })

    await wrapper.findAll('.dragHandle')[0].trigger('mouseup')

    expect(dvMainStoreMock.setInEditorStatus).toHaveBeenCalledWith(true)
    expect(dvMainStoreMock.setClickComponentStatus).toHaveBeenCalledWith(true)
    expect(dvMainStoreMock.setCurComponent).toHaveBeenCalledWith({
      component: item,
      index: 2
    })
  })

  it('emits componentClick on the event bus after the next tick', async () => {
    const wrapper = mount(DbDragArea, {
      props: { item, index: 0 }
    })

    await wrapper.findAll('.dragHandle')[1].trigger('mouseup')
    await nextTick()

    expect(eventBusMock.emit).toHaveBeenCalledWith('componentClick')
  })
})
