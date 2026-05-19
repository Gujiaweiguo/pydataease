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
vi.mock('@/utils/color', () => ({ getCSSVariable: () => '#3370ff' }))
vi.mock('@/views/chart/components/js/formatter', () => ({
  formatterItem: { type: 'auto', unit: 1, suffix: '', decimalCount: 2, thousandSeparator: true }
}))
vi.mock('@element-plus/icons-vue', () => ({
  Delete: { template: '<i />' },
  Filter: { template: '<i />' }
}))
vi.mock('@/assets/svg/icon_delete-trash_outlined.svg', () => ({ default: 'icon_delete' }))
vi.mock('@/assets/svg/icon_down_outlined-1.svg', () => ({ default: 'icon_down' }))

import FilterItem from '../FilterItem.vue'

const globalStubs = {
  ElDropdown: {
    template: '<div class="el-dropdown"><slot /><slot name="dropdown" /></div>',
    props: ['effect']
  },
  ElDropdownMenu: { template: '<div><slot /></div>' },
  ElDropdownItem: { template: '<div><slot /></div>', props: ['command', 'icon', 'divided'] },
  ElTag: { template: '<span><slot /></span>' },
  ElIcon: { template: '<i><slot /></i>' },
  Icon: { template: '<span><slot /></span>', props: ['name', 'className', 'class-name'] }
}

const defaultProps = () => ({
  item: { id: '1', name: 'filter_field', deType: 0 },
  index: 0,
  dimensionData: [
    {
      id: '1',
      name: 'filter_field',
      deType: 0,
      groupType: 'd',
      originName: 'filter_field',
      dataeaseName: 'ff'
    }
  ],
  quotaData: [],
  themes: 'dark'
})

describe('FilterItem', () => {
  it('renders with required props', () => {
    const wrapper = shallowMount(FilterItem, {
      props: defaultProps(),
      global: { stubs: globalStubs, mocks: { $t: (k: string) => k } }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.item-style').exists()).toBe(true)
  })

  it('renders item name in the span', () => {
    const wrapper = shallowMount(FilterItem, {
      props: defaultProps(),
      global: { stubs: globalStubs, mocks: { $t: (k: string) => k } }
    })
    expect(wrapper.html()).toContain('filter_field')
  })

  it('emits onFilterItemRemove when removeItem is called', () => {
    const wrapper = shallowMount(FilterItem, {
      props: defaultProps(),
      global: { stubs: globalStubs, mocks: { $t: (k: string) => k } }
    })
    wrapper.vm.removeItem()
    expect(wrapper.emitted('onFilterItemRemove')).toBeTruthy()
    const emittedArg = wrapper.emitted('onFilterItemRemove')![0][0] as any
    expect(emittedArg.index).toBe(0)
  })

  it('emits editItemFilter when editFilter is called', () => {
    const wrapper = shallowMount(FilterItem, {
      props: defaultProps(),
      global: { stubs: globalStubs, mocks: { $t: (k: string) => k } }
    })
    wrapper.vm.editFilter()
    expect(wrapper.emitted('editItemFilter')).toBeTruthy()
  })

  it('clickItem does nothing with null param', () => {
    const wrapper = shallowMount(FilterItem, {
      props: defaultProps(),
      global: { stubs: globalStubs, mocks: { $t: (k: string) => k } }
    })
    wrapper.vm.clickItem(null)
    expect(wrapper.emitted('onFilterItemRemove')).toBeFalsy()
    expect(wrapper.emitted('editItemFilter')).toBeFalsy()
  })

  it('clickItem dispatches remove', () => {
    const wrapper = shallowMount(FilterItem, {
      props: defaultProps(),
      global: { stubs: globalStubs, mocks: { $t: (k: string) => k } }
    })
    wrapper.vm.clickItem({ type: 'remove' })
    expect(wrapper.emitted('onFilterItemRemove')).toBeTruthy()
  })
})
