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
vi.mock('@/assets/svg/icon_delete-trash_outlined.svg', () => ({ default: 'icon_delete' }))
vi.mock('@/assets/svg/icon_down_outlined-1.svg', () => ({ default: 'icon_down' }))
vi.mock('@/assets/svg/icon_sort-a-to-z_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_sort-z-to-a_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_sort_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_right_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_done_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_edit_outlined.svg', () => ({ default: 'icon' }))

import DrillItem from '../DrillItem.vue'

const globalStubs = {
  ElDropdown: {
    template: '<div class="el-dropdown"><slot /><slot name="dropdown" /></div>',
    props: ['effect', 'size']
  },
  ElDropdownMenu: { template: '<div><slot /></div>' },
  ElDropdownItem: { template: '<div><slot /></div>', props: ['command', 'divided', 'class'] },
  ElTag: { template: '<span><slot /></span>' },
  ElIcon: { template: '<i><slot /></i>' },
  ElTooltip: { template: '<div><slot /><slot #content /></div>' },
  Icon: { template: '<span><slot /></span>', props: ['name', 'className'] }
}

const defaultProps = () => ({
  item: { id: '1', name: 'drill_field', deType: 0, sort: 'none', groupType: 'd', customSort: [] },
  index: 0,
  chart: { type: 'bar' },
  dimensionData: [
    {
      id: '1',
      name: 'drill_field',
      deType: 0,
      groupType: 'd',
      originName: 'drill_field',
      dataeaseName: 'df'
    }
  ],
  quotaData: [],
  themes: 'dark'
})

describe('DrillItem', () => {
  it('renders with required props', () => {
    const wrapper = shallowMount(DrillItem, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.item-style').exists()).toBe(true)
  })

  it('renders item chartShowName when available', () => {
    const props = defaultProps()
    props.item.chartShowName = 'drill display'
    const wrapper = shallowMount(DrillItem, {
      props,
      global: { stubs: globalStubs }
    })
    expect(wrapper.html()).toContain('drill display')
  })

  it('emits onDimensionItemRemove on removeItem', () => {
    const wrapper = shallowMount(DrillItem, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    wrapper.vm.removeItem()
    expect(wrapper.emitted('onDimensionItemRemove')).toBeTruthy()
  })

  it('emits onNameEdit on showRename', () => {
    const wrapper = shallowMount(DrillItem, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    wrapper.vm.showRename()
    const emitted = wrapper.emitted('onNameEdit')![0][0] as any
    expect(emitted.renameType).toBe('drillFields')
  })

  it('emits onCustomSort when sort called with custom_sort', () => {
    const wrapper = shallowMount(DrillItem, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    wrapper.vm.sort({ type: 'custom_sort' })
    expect(wrapper.emitted('onCustomSort')).toBeTruthy()
  })

  it('emits onDimensionItemChange when sort called with non-custom type', () => {
    const wrapper = shallowMount(DrillItem, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    wrapper.vm.sort({ type: 'asc' })
    expect(wrapper.emitted('onDimensionItemChange')).toBeTruthy()
  })

  it('clickItem dispatches sortPriority', () => {
    const wrapper = shallowMount(DrillItem, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    wrapper.vm.clickItem({ type: 'sortPriority' })
    expect(wrapper.emitted('editSortPriority')).toBeTruthy()
  })
})
