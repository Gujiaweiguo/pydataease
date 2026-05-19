import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => key })
}))

import DrawerMain from '@/components/drawer-main/src/DrawerMain.vue'

const clearMocks = [vi.fn(), vi.fn(), vi.fn(), vi.fn()]

const filterStubs = {
  DrawerTreeFilter: defineComponent({
    name: 'DrawerTreeFilter',
    emits: ['filter-change'],
    methods: { clear: clearMocks[0] },
    template: '<div class="tree-filter"></div>'
  }),
  DrawerFilter: defineComponent({
    name: 'DrawerFilter',
    emits: ['filter-change'],
    methods: { clear: clearMocks[1] },
    template: '<div class="select-filter"></div>'
  }),
  DrawerEnumFilter: defineComponent({
    name: 'DrawerEnumFilter',
    emits: ['filter-change'],
    methods: { clear: clearMocks[2] },
    template: '<div class="enum-filter"></div>'
  }),
  DrawerTimeFilter: defineComponent({
    name: 'DrawerTimeFilter',
    emits: ['filter-change'],
    methods: { clear: clearMocks[3] },
    template: '<div class="time-filter"></div>'
  }),
  ElDrawer: defineComponent({
    name: 'ElDrawer',
    props: ['modelValue', 'title'],
    template:
      '<div class="drawer-stub" :data-open="String(modelValue)"><slot /><slot name="footer" /></div>'
  }),
  ElButton: defineComponent({
    name: 'ElButton',
    emits: ['click'],
    template: '<button class="button-stub" @click="$emit(\'click\')"><slot /></button>'
  })
}

const options = [
  { type: 'tree-select', field: 'tree', option: [], title: 'Tree', property: {} },
  { type: 'select', field: 'city', option: [], title: 'City', property: {} },
  { type: 'enum', field: 'status', option: [], title: 'Status', property: {} },
  {
    type: 'time',
    field: 'created',
    option: [],
    title: 'Created',
    property: {},
    operator: 'between'
  }
]

const mountComponent = () =>
  mount(DrawerMain, {
    props: { filterOptions: options, title: 'Filters' },
    global: { stubs: filterStubs }
  })

describe('DrawerMain', () => {
  it('renders filter components for each supported type', () => {
    const wrapper = mountComponent()

    expect(wrapper.find('.tree-filter').exists()).toBe(true)
    expect(wrapper.find('.select-filter').exists()).toBe(true)
    expect(wrapper.find('.enum-filter').exists()).toBe(true)
    expect(wrapper.find('.time-filter').exists()).toBe(true)
  })

  it('opens the drawer when init is called', async () => {
    const wrapper = mountComponent()

    ;(wrapper.vm as any).init()
    await wrapper.vm.$nextTick()

    expect(wrapper.get('.drawer-stub').attributes('data-open')).toBe('true')
  })

  it('emits filter changes from child filters', async () => {
    const wrapper = mountComponent()

    await wrapper.getComponent({ name: 'DrawerFilter' }).vm.$emit('filter-change', ['beijing'])

    expect(wrapper.emitted('tree-filter-change')).toEqual([
      [{ value: ['beijing'], field: 'city', operator: 'in' }]
    ])
  })
})
