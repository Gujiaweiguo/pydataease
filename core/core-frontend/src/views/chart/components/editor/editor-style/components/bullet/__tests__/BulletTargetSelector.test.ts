import { describe, it, expect, vi, beforeEach } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import BulletTargetSelector from '../BulletTargetSelector.vue'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/views/chart/components/editor/util/chart', () => ({
  COLOR_PANEL: ['#000000', '#ffffff'],
  DEFAULT_MISC: {
    bullet: {
      bar: {
        target: {
          fill: 'rgb(0,0,0)',
          size: 20,
          showType: 'dynamic',
          value: 0,
          name: ''
        }
      }
    }
  }
}))

const createWrapper = (overrides = {}) => {
  return shallowMount(BulletTargetSelector, {
    props: {
      chart: {
        customAttr: {
          misc: {
            bullet: {
              bar: {
                target: {
                  fill: 'rgb(0,0,0)',
                  size: 20,
                  showType: 'dynamic',
                  value: 0,
                  name: ''
                }
              }
            }
          }
        }
      },
      selectorType: 'target',
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
        'el-input-number': { template: '<input type="number" />' }
      }
    }
  })
}

describe('BulletTargetSelector', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders when selectorType is target', () => {
    const wrapper = createWrapper({ selectorType: 'target' })
    expect(wrapper.find('form').exists()).toBe(true)
  })

  it('does not render target section when selectorType is not target', () => {
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
    vm.changeStyle('bar.target.fill')
    const miscChangeEvents = wrapper.emitted('onMiscChange')
    expect(miscChangeEvents).toBeTruthy()
    expect(miscChangeEvents?.[0]?.[1]).toBe('bar.target.fill')
  })

  it('sets null value to 1 when changeStyle is called with null target value', async () => {
    const wrapper = createWrapper()
    const vm = wrapper.vm as any
    vm.state.bulletTargetForm.bar.target.value = null
    vm.changeStyle()
    expect(vm.state.bulletTargetForm.bar.target.value).toBe(1)
  })

  it('emits onMiscChange with data containing bullet form', async () => {
    const wrapper = createWrapper()
    const vm = wrapper.vm as any
    vm.changeStyle()
    const emittedArgs = wrapper.emitted('onMiscChange')?.[0] || []
    expect(emittedArgs[0].data).toHaveProperty('bullet')
    expect(emittedArgs[0].requestData).toBe(true)
  })
})
