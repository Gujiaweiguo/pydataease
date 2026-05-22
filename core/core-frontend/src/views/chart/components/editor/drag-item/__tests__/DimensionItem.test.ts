import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/utils/attr', () => ({
  fieldType: ['text', 'time', 'value', 'value', 'value', 'location', 'binary', 'url']
}))
vi.mock('@/components/icon-group/field-list', () => ({ iconFieldMap: {} }))
vi.mock('@/views/chart/components/editor/drag-item/utils', () => ({
  getItemType: () => '#3370ff'
}))
vi.mock('@/assets/svg/icon_sort-a-to-z_outlined.svg', () => ({ default: 'icon_sortAToZ' }))
vi.mock('@/assets/svg/icon_sort-z-to-a_outlined.svg', () => ({ default: 'icon_sortZToA' }))
vi.mock('@/assets/svg/icon_sort_outlined.svg', () => ({ default: 'icon_sort' }))
vi.mock('@/assets/svg/icon_delete-trash_outlined.svg', () => ({ default: 'icon_delete' }))
vi.mock('@/assets/svg/icon_down_outlined-1.svg', () => ({ default: 'icon_down' }))
vi.mock('@/assets/svg/icon_right_outlined.svg', () => ({ default: 'icon_right' }))
vi.mock('@/assets/svg/icon_done_outlined.svg', () => ({ default: 'icon_done' }))
vi.mock('@/assets/svg/icon_edit_outlined.svg', () => ({ default: 'icon_edit' }))
vi.mock('@/assets/svg/icon_visible_outlined.svg', () => ({ default: 'icon_visible' }))
vi.mock('@/assets/svg/icon_invisible_outlined.svg', () => ({ default: 'icon_invisible' }))

import DimensionItem from '../DimensionItem.vue'

const globalStubs = {
  ElDropdown: {
    template: '<div class="el-dropdown"><slot /><slot name="dropdown" /></div>',
    props: ['effect']
  },
  ElDropdownMenu: { template: '<div><slot /></div>' },
  ElDropdownItem: { template: '<div><slot /></div>', props: ['command', 'divided', 'icon'] },
  ElTag: { template: '<span><slot /></span>', props: ['class', 'style'] },
  ElIcon: { template: '<i><slot /></i>' },
  ElTooltip: { template: '<div><slot /><slot #content /></div>' },
  Icon: { template: '<span><slot /></span>', props: ['name', 'className'] }
}

const defaultProps = () => ({
  item: {
    id: '1',
    name: 'field1',
    deType: 0,
    sort: 'none',
    groupType: 'd',
    dateStyle: 'y',
    datePattern: 'date_sub'
  },
  index: 0,
  chart: { type: 'bar' },
  dimensionData: [
    { id: '1', name: 'field1', deType: 0, groupType: 'd', originName: 'field1', dataeaseName: 'f1' }
  ],
  quotaData: [],
  themes: 'dark',
  type: 'dimension'
})

describe('DimensionItem', () => {
  it('renders with required props', () => {
    const wrapper = shallowMount(DimensionItem, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.item-style').exists()).toBe(true)
  })

  it('renders the item name via chartShowName or name', () => {
    const props = defaultProps()
    ;(props.item as Record<string, any>).chartShowName = 'display name'
    const wrapper = shallowMount(DimensionItem, {
      props,
      global: { stubs: globalStubs }
    })
    expect(wrapper.html()).toContain('display name')
  })

  it('emits onDimensionItemRemove when removeItem is called', async () => {
    const wrapper = shallowMount(DimensionItem, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    ;(wrapper.vm as any).removeItem()
    expect(wrapper.emitted('onDimensionItemRemove')).toBeTruthy()
  })

  it('computes showSort correctly for unsupported types', () => {
    const props = defaultProps()
    props.chart.type = 'word-cloud'
    const wrapper = shallowMount(DimensionItem, {
      props,
      global: { stubs: globalStubs }
    })
    expect((wrapper.vm as any).showSort).toBe(false)
  })

  it('computes showSort correctly for supported types', () => {
    const props = defaultProps()
    props.chart.type = 'bar'
    props.type = 'dimension'
    const wrapper = shallowMount(DimensionItem, {
      props,
      global: { stubs: globalStubs }
    })
    expect((wrapper.vm as any).showSort).toBe(true)
  })

  it('showValueFormatter is true for table types with numeric deType', () => {
    const props = defaultProps()
    props.chart.type = 'table-normal'
    props.item.deType = 2
    const wrapper = shallowMount(DimensionItem, {
      props,
      global: { stubs: globalStubs }
    })
    expect((wrapper.vm as any).showValueFormatter).toBe(true)
  })

  it('toolTip computed returns themes value', () => {
    const props = defaultProps()
    props.themes = 'light'
    const wrapper = shallowMount(DimensionItem, {
      props,
      global: { stubs: globalStubs }
    })
    expect((wrapper.vm as any).toolTip).toBe('light')
  })
})
