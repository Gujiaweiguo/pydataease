import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import BulletMeasureSelector from '../BulletMeasureSelector.vue'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#000000', '#ffffff'],
  DEFAULT_MISC: {
    bullet: {
      bar: {
        measures: {
          fill: 'rgba(0,128,255,1)',
          size: 15,
          name: ''
        }
      }
    }
  }
}))

const createWrapper = (overrides = {}) => {
  return shallowMount(BulletMeasureSelector, {
    props: {
      chart: {
        customAttr: {
          misc: {
            bullet: {
              bar: {
                measures: {
                  fill: 'rgba(0,128,255,1)',
                  size: 15,
                  name: ''
                }
              }
            }
          }
        }
      },
      selectorType: 'measure',
      themes: 'dark',
      ...overrides
    },
    global: {
      stubs: {
        'el-form': { template: '<form><slot /></form>' },
        'el-form-item': { template: '<div><slot /></div>' },
        'el-color-picker': { template: '<input type="color" />' },
        'el-input-number': { template: '<input type="number" />' }
      }
    }
  })
}

describe('BulletMeasureSelector', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders when selectorType is measure', () => {
    const wrapper = createWrapper({ selectorType: 'measure' })
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('does not render measure section when selectorType is not measure', () => {
    const wrapper = createWrapper({ selectorType: 'range' })

    const measureDiv = wrapper.find('div[style*="flex: 1"]')
    expect(measureDiv.exists()).toBe(false)
  })

  it('accepts chart prop as required', () => {
    const wrapper = createWrapper()
    expect(wrapper.props('chart')).toBeDefined()
  })

  it('accepts themes prop with default dark', () => {
    const wrapper = createWrapper()
    expect(wrapper.props('themes')).toBe('dark')
  })

  it('accepts themes prop with light value', () => {
    const wrapper = createWrapper({ themes: 'light' })
    expect(wrapper.props('themes')).toBe('light')
  })

  it('emits onMiscChange when changeStyle is called', async () => {
    const wrapper = createWrapper()
    const vm = wrapper.vm as any
    vm.changeStyle('bar.measures.fill')
    expect(wrapper.emitted('onMiscChange')).toBeTruthy()
    expect(wrapper.emitted('onMiscChange')![0][1]).toBe('bar.measures.fill')
  })

  it('emits onMiscChange with data containing bullet form', async () => {
    const wrapper = createWrapper()
    const vm = wrapper.vm as any
    vm.changeStyle()
    const emittedArgs = wrapper.emitted('onMiscChange')![0]
    expect(emittedArgs[0].data).toHaveProperty('bullet')
    expect(emittedArgs[0].requestData).toBe(true)
  })
})
