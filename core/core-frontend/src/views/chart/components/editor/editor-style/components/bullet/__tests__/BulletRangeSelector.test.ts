import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import BulletRangeSelector from '../BulletRangeSelector.vue'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#000000', '#ffffff', '#ff0000', '#00ff00'],
  DEFAULT_MISC: {
    bullet: {
      bar: {
        ranges: {
          fill: 'rgba(0,128,255,0.5)',
          size: 20,
          showType: 'dynamic',
          fixedRange: [],
          fixedRangeNumber: 3,
          symbol: 'circle',
          symbolSize: 10,
          name: ''
        }
      }
    }
  }
}))

const createWrapper = (overrides = {}) => {
  return shallowMount(BulletRangeSelector, {
    props: {
      chart: {
        customAttr: {
          misc: {
            bullet: {
              bar: {
                ranges: {
                  fill: 'rgba(0,128,255,0.5)',
                  size: 20,
                  showType: 'dynamic',
                  fixedRange: [],
                  fixedRangeNumber: 3,
                  symbol: 'circle',
                  symbolSize: 10,
                  name: ''
                }
              }
            }
          }
        }
      },
      selectorType: 'range',
      themes: 'dark',
      ...overrides
    },
    global: {
      stubs: {
        'el-form': { template: '<form><slot /></form>' },
        'el-form-item': { template: '<div><slot /></div>' },
        'el-radio-group': { template: '<div><slot /></div>' },
        'el-radio': { template: '<label><slot /></label>' },
        'el-color-picker': { template: '<input type="color" />' },
        'el-input-number': { template: '<input type="number" />' },
        'el-input': { template: '<input />' }
      }
    }
  })
}

describe('BulletRangeSelector', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders when selectorType is range', () => {
    const wrapper = createWrapper({ selectorType: 'range' })
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('does not render range section when selectorType is not range', () => {
    const wrapper = createWrapper({ selectorType: 'measure' })
    const formItems = wrapper.findAll('.form-item')
    expect(formItems.length).toBe(0)
  })

  it('accepts chart prop as required', () => {
    const wrapper = createWrapper()
    expect(wrapper.props('chart')).toBeDefined()
  })

  it('accepts themes prop with default dark', () => {
    const wrapper = createWrapper()
    expect(wrapper.props('themes')).toBe('dark')
  })

  it('emits onMiscChange when changeStyle is called', async () => {
    const wrapper = createWrapper()
    const vm = wrapper.vm as any
    vm.changeStyle('bar.ranges.size')
    expect(wrapper.emitted('onMiscChange')).toBeTruthy()
    expect(wrapper.emitted('onMiscChange')![0][1]).toBe('bar.ranges.size')
  })

  it('emits onMiscChange with data containing bullet form', async () => {
    const wrapper = createWrapper()
    const vm = wrapper.vm as any
    vm.changeStyle()
    const emittedArgs = wrapper.emitted('onMiscChange')![0]
    expect(emittedArgs[0].data).toHaveProperty('bullet')
    expect(emittedArgs[0].requestData).toBe(true)
  })

  it('handles fixedRangeNumber null by defaulting to 1', async () => {
    const wrapper = createWrapper()
    const vm = wrapper.vm as any
    vm.state.bulletRangeForm.bar.ranges.fixedRangeNumber = null
    vm.changeRangeNumber()
    expect(vm.state.bulletRangeForm.bar.ranges.fixedRangeNumber).toBe(1)
  })

  it('validates range list items with empty names', async () => {
    const wrapper = createWrapper()
    const vm = wrapper.vm as any
    vm.state.rangeList = [{ name: '', fixedRangeValue: null, fill: '#000' }]
    const result = vm.validateRangeList()
    expect(result).toBe(true)
    expect(vm.state.rangeList[0].fixedRangeValue).toBe(0)
    expect(vm.state.rangeList[0].name).toBeTruthy()
  })
})
