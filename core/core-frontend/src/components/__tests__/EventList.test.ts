import { defineComponent, ref } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  addEvent: vi.fn(),
  removeEvent: vi.fn(),
  curComponent: null as any
}))

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: (store: Record<string, unknown>) => store
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({ curComponent: mocks.curComponent })
}))

vi.mock('@/store/modules/data-visualization/event', () => ({
  eventStoreWithOut: () => ({
    addEvent: mocks.addEvent,
    removeEvent: mocks.removeEvent
  })
}))

vi.mock('@/utils/events', () => ({
  eventList: [
    { key: 'redirect', label: 'Redirect', param: 'https://a.com' },
    { key: 'alert', label: 'Alert', param: 'hello' }
  ]
}))

vi.mock('@/components/data-visualization/Modal.vue', () => ({
  default: defineComponent({
    name: 'Modal',
    props: ['modelValue', 'show'],
    template: '<div v-if="modelValue ?? show" class="modal-stub"><slot /></div>'
  })
}))

import EventList from '@/components/data-visualization/EventList.vue'

const globalStubs = {
  ElButton: defineComponent({
    name: 'ElButton',
    emits: ['click'],
    template: '<button class="button-stub" @click="$emit(\'click\')"><slot /></button>'
  }),
  ElTag: defineComponent({
    name: 'ElTag',
    emits: ['close'],
    template: '<span class="tag-stub" @click="$emit(\'close\')"><slot /></span>'
  }),
  ElTabs: defineComponent({ name: 'ElTabs', template: '<div><slot /></div>' }),
  ElTabPane: defineComponent({
    name: 'ElTabPane',
    template: '<div class="pane-stub"><slot /></div>'
  }),
  ElInput: defineComponent({
    name: 'ElInput',
    template: '<textarea class="input-stub"></textarea>'
  })
}

describe('EventList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // ref already imported at top
    mocks.curComponent = ref({ events: { redirect: 'url', alert: 'warn' } })
  })

  it('renders existing event tags from the current component', () => {
    const wrapper = shallowMount(EventList, { global: { stubs: globalStubs } })

    expect(wrapper.findAll('.tag-stub')).toHaveLength(2)
    expect(wrapper.text()).toContain('redirect')
    expect(wrapper.text()).toContain('alert')
  })

  it('removes an event when a tag is closed', async () => {
    const wrapper = shallowMount(EventList, { global: { stubs: globalStubs } })

    await wrapper.findAll('.tag-stub')[0].trigger('click')

    expect(mocks.removeEvent).toHaveBeenCalledWith('redirect')
  })

  it('renders the add-event action button', () => {
    const wrapper = shallowMount(EventList, { global: { stubs: globalStubs } })

    expect(wrapper.findAll('.button-stub')).toHaveLength(1)
    expect(wrapper.text()).toContain('添加事件')
  })
})
