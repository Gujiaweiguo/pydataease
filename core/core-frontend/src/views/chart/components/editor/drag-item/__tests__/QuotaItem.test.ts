import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/utils/attr', () => ({
  fieldType: ['text', 'time', 'value', 'value', 'value', 'location', 'binary', 'url']
}))
vi.mock('@/components/icon-group/field-list', () => ({ iconFieldMap: {} }))
vi.mock('@/views/chart/components/editor/drag-item/utils', () => ({
  getItemType: () => '#04b49c',
  resetValueFormatter: vi.fn()
}))
vi.mock('@/views/chart/components/js/formatter', () => ({
  formatterItem: { type: 'auto', unit: 1, suffix: '', decimalCount: 2, thousandSeparator: true }
}))
vi.mock('@/views/chart/components/js/util', () => ({
  quotaViews: [],
  notSupportAccumulateViews: []
}))
vi.mock('@/views/chart/components/editor/util/chart', () => ({
  SUPPORT_Y_M: ['y', 'y_M']
}))
vi.mock('@/assets/svg/icon_sort-a-to-z_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_sort-z-to-a_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_sort_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_delete-trash_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_down_outlined-1.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_right_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_done_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_functions_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_visible_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_invisible_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon_edit_outlined.svg', () => ({ default: 'icon' }))
vi.mock('@/assets/svg/icon-filter.svg', () => ({ default: 'icon' }))

import QuotaItem from '../QuotaItem.vue'

const globalStubs = {
  ElDropdown: {
    template: '<div class="el-dropdown"><slot /><slot name="dropdown" /></div>',
    props: ['effect']
  },
  ElDropdownMenu: { template: '<div><slot /></div>' },
  ElDropdownItem: {
    template: '<div><slot /></div>',
    props: ['command', 'divided', 'icon', 'disabled']
  },
  ElTag: { template: '<span><slot /></span>' },
  ElIcon: { template: '<i><slot /></i>' },
  ElTooltip: { template: '<div><slot /><slot #content /></div>' },
  Icon: { template: '<span><slot /></span>', props: ['name', 'className', 'class-name'] }
}

const defaultProps = () => ({
  item: {
    id: '1',
    name: 'qty',
    deType: 2,
    sort: 'none',
    groupType: 'q',
    summary: 'sum',
    compareCalc: { type: 'none' },
    formatterCfg: { type: 'auto', unit: 1, suffix: '', decimalCount: 2, thousandSeparator: true },
    customSort: []
  },
  index: 0,
  chart: { type: 'bar', xAxis: '[]', xAxisExt: '[]' },
  dimensionData: [],
  quotaData: [
    { id: '1', name: 'qty', deType: 2, groupType: 'q', originName: 'qty', dataeaseName: 'q1' }
  ],
  themes: 'dark',
  type: 'quota'
})

describe('QuotaItem', () => {
  it('renders with required props', () => {
    const wrapper = shallowMount(QuotaItem, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.item-style').exists()).toBe(true)
  })

  it('renders item name from chartShowName when available', () => {
    const props = defaultProps()
    ;(props.item as Record<string, any>).chartShowName = 'display qty'
    const wrapper = shallowMount(QuotaItem, {
      props,
      global: { stubs: globalStubs }
    })
    expect(wrapper.html()).toContain('display qty')
  })

  it('emits onQuotaItemRemove when removeItem is called', () => {
    const wrapper = shallowMount(QuotaItem, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    ;(wrapper.vm as any).removeItem()
    expect(wrapper.emitted('onQuotaItemRemove')).toBeTruthy()
  })

  it('showSort is false for multi-scatter type', () => {
    const props = defaultProps()
    props.chart.type = 'multi-scatter'
    const wrapper = shallowMount(QuotaItem, {
      props,
      global: { stubs: globalStubs }
    })
    expect((wrapper.vm as any).showSort).toBe(false)
  })

  it('showSort is false for extLabel/extTooltip/extBubble types', () => {
    const props = defaultProps()
    props.type = 'extLabel'
    const wrapper = shallowMount(QuotaItem, {
      props,
      global: { stubs: globalStubs }
    })
    expect((wrapper.vm as any).showSort).toBe(false)
  })

  it('emits editItemFilter when editFilter is called', () => {
    const wrapper = shallowMount(QuotaItem, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    ;(wrapper.vm as any).editFilter()
    expect(wrapper.emitted('editItemFilter')).toBeTruthy()
  })

  it('handles undefined chart type during reactive updates', async () => {
    const props = defaultProps()
    const wrapper = shallowMount(QuotaItem, {
      props,
      global: { stubs: globalStubs }
    })

    await wrapper.setProps({
      chart: undefined as unknown as { type: string; xAxis: string; xAxisExt: string }
    })

    expect(wrapper.exists()).toBe(true)
    expect((wrapper.vm as any).showValueFormatter).toBe(false)
  })

  it('does not crash when item.compareCalc is undefined', async () => {
    const props = defaultProps()
    delete (props.item as Record<string, any>).compareCalc
    const wrapper = shallowMount(QuotaItem, {
      props,
      global: { stubs: globalStubs }
    })

    await wrapper.setProps({
      chart: { type: 'gauge', xAxis: '[]', xAxisExt: '[]' }
    })

    expect(wrapper.exists()).toBe(true)
  })
})
