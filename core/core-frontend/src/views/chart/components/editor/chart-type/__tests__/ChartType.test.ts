import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

vi.mock('@/config/axios/service', () => ({ service: {} as any, PATH_URL: './', cancelMap: new Map() }))
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/store', () => ({ store: {} }))
vi.mock('pinia', () => ({ defineStore: vi.fn(), storeToRefs: vi.fn(() => ({})), createPinia: vi.fn() }))

vi.mock('@/views/chart/components/editor/util/chart', () => ({
  CHART_TYPE_CONFIGS: [
    {
      category: 'quota',
      title: '指标',
      display: 'show',
      details: [
        { title: '柱状图', render: 'antv', value: 'bar', icon: 'bar' },
        { title: '折线图', render: 'antv', value: 'line', icon: 'line' }
      ]
    }
  ]
}))

vi.mock('@/components/icon-custom/src/Icon.vue', () => ({
  default: { template: '<span class="icon-stub"><slot /></span>' }
}))

vi.mock('@/components/icon-group/chart-dark-list', () => ({
  iconChartDarkMap: {}
}))

vi.mock('@/components/icon-group/chart-list', () => ({
  iconChartMap: {}
}))

describe('ChartType', () => {
  it('renders without errors', async () => {
    const ChartType = (await import('../ChartType.vue')).default
    const wrapper = shallowMount(ChartType, {
      props: {
        type: 'bar',
        themes: 'dark'
      },
      global: {
        stubs: {
          'el-row': { template: '<div class="el-row"><slot /></div>' },
          'el-col': { template: '<div class="el-col"><slot /></div>' },
          'el-scrollbar': { template: '<div class="el-scrollbar"><slot /></div>' },
          Icon: { template: '<span class="icon-stub"><slot /></span>' }
        }
      }
    })
    expect(wrapper.find('.el-row').exists()).toBe(true)
  })

  it('accepts required type prop', async () => {
    const ChartType = (await import('../ChartType.vue')).default
    const wrapper = shallowMount(ChartType, {
      props: {
        type: 'line'
      },
      global: {
        stubs: {
          'el-row': { template: '<div><slot /></div>' },
          'el-col': { template: '<div><slot /></div>' },
          'el-scrollbar': { template: '<div><slot /></div>' },
          Icon: { template: '<span><slot /></span>' }
        }
      }
    })
    expect(wrapper.props('type')).toBe('line')
  })

  it('emits onTypeChange when newComponent is called', async () => {
    const ChartType = (await import('../ChartType.vue')).default
    const wrapper = shallowMount(ChartType, {
      props: {
        type: 'bar'
      },
      global: {
        stubs: {
          'el-row': { template: '<div><slot /></div>' },
          'el-col': { template: '<div><slot /></div>' },
          'el-scrollbar': { template: '<div><slot /></div>' },
          Icon: { template: '<span><slot /></span>' }
        }
      }
    })
    const vm = wrapper.vm as any
    vm.newComponent('antv', 'line')
    expect(wrapper.emitted('onTypeChange')).toBeTruthy()
    expect(wrapper.emitted('onTypeChange')![0]).toEqual(['antv', 'line'])
  })
})
