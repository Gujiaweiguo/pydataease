import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/views/chart/components/js/panel', () => ({
  default: {
    getChartView: () => ({
      axis: ['xAxis', 'yAxis']
    })
  }
}))
vi.mock('vuedraggable', () => ({
  default: { template: '<div><slot /></div>', props: ['list', 'itemKey', 'animation'] }
}))

import SortPriorityEdit from '../SortPriorityEdit.vue'

const globalStubs = {
  ElScrollbar: { template: '<div><slot /></div>', props: ['height', 'maxHeight'] },
  ElIcon: { template: '<i><slot /></i>' },
  Icon: { template: '<span><slot /></span>', props: ['name'] }
}

const defaultProps = () => ({
  chart: {
    id: 'chart1',
    type: 'bar',
    render: 'antv',
    sortPriority: [],
    xAxis: [{ id: 'x1', name: 'X Field', chartShowName: undefined }],
    yAxis: [{ id: 'y1', name: 'Y Field', chartShowName: undefined }],
    xAxisExt: [],
    yAxisExt: [],
    extBubble: [],
    flowMapEndName: [],
    flowMapStartName: [],
    extColor: [],
    extStack: [],
    drillFields: []
  }
})

describe('SortPriorityEdit', () => {
  it('renders with required props', () => {
    const wrapper = shallowMount(SortPriorityEdit, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('initializes sortList from chart axis data', () => {
    const wrapper = shallowMount(SortPriorityEdit, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    expect(vm.state.sortList).toBeDefined()
    // Should contain items from xAxis and yAxis
    expect(vm.state.sortList.length).toBeGreaterThanOrEqual(2)
  })

  it('emits onPriorityChange when onUpdate is called', () => {
    const wrapper = shallowMount(SortPriorityEdit, {
      props: defaultProps(),
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    vm.onUpdate()
    expect(wrapper.emitted('onPriorityChange')).toBeTruthy()
  })

  it('preserves existing sortPriority order when provided', () => {
    const props = defaultProps()
    props.chart.sortPriority = [{ id: 'y1', name: 'Y Field' }]
    const wrapper = shallowMount(SortPriorityEdit, {
      props,
      global: { stubs: globalStubs }
    })
    const vm = wrapper.vm as any
    // y1 should be first since it was in sortPriority
    expect(vm.state.sortList[0].id).toBe('y1')
  })
})
