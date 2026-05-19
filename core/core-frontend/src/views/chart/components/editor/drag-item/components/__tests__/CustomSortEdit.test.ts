import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/api/chart', () => ({
  getFieldData: () => Promise.resolve({ data: ['item1', 'item2', 'item3'] }),
  getDrillFieldData: () => Promise.resolve({ data: ['drill1', 'drill2'] })
}))
vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({ wsCache: { get: () => 'test-uid' } })
}))
vi.mock('vuedraggable', () => ({
  default: { template: '<div><slot /></div>', props: ['list', 'itemKey', 'animation'] }
}))

import CustomSortEdit from '../CustomSortEdit.vue'

const globalStubs = {
  ElScrollbar: { template: '<div><slot /></div>', props: ['height', 'maxHeight'] },
  ElIcon: { template: '<i><slot /></i>' },
  Icon: { template: '<span><slot /></span>', props: ['name'] }
}

const defaultProps = () => ({
  chart: { id: 'chart1', chartExtRequest: null },
  field: { id: 'field1', name: 'Test Field' },
  fieldType: 'xAxis',
  originSortList: []
})

describe('CustomSortEdit', () => {
  it('renders with required props', () => {
    const wrapper = shallowMount(CustomSortEdit, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('initializes with loading state', () => {
    const wrapper = shallowMount(CustomSortEdit, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.state.sortList).toBeDefined()
  })

  it('emits onSortChange after init loads data', async () => {
    const wrapper = shallowMount(CustomSortEdit, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    // Wait for the async init to complete
    await new Promise(resolve => setTimeout(resolve, 50))
    expect(wrapper.emitted('onSortChange')).toBeTruthy()
  })
})
