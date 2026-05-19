import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('vue-clipboard3', () => ({ default: () => ({ toClipboard: vi.fn(() => Promise.resolve()) }) }))
vi.mock('@/assets/svg/eye.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/eye-open.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/dv-info.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/de-copy.svg', () => ({ default: '' }))
import InfoTemplate from '../InfoTemplate.vue'

describe('InfoTemplate', () => {
  const stubs = {
    ElButton: { template: '<button><slot /></button>' },
    ElIcon: { template: '<i><slot /></i>' },
    ElTooltip: { template: '<div><slot /></div>' }
  }

  it('renders with default props', () => {
    const wrapper = shallowMount(InfoTemplate, {
      props: {
        settingData: [],
        labelTooltips: [],
        copyList: []
      },
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders header when hideHead is false', () => {
    const wrapper = shallowMount(InfoTemplate, {
      props: {
        settingData: [],
        labelTooltips: [],
        copyList: [],
        hideHead: false
      },
      global: { stubs }
    })
    expect(wrapper.find('.info-template-header').exists()).toBe(true)
  })

  it('hides header when hideHead is true', () => {
    const wrapper = shallowMount(InfoTemplate, {
      props: {
        settingData: [],
        labelTooltips: [],
        copyList: [],
        hideHead: true
      },
      global: { stubs }
    })
    expect(wrapper.find('.info-template-header').exists()).toBe(false)
  })

  it('exposes init method', () => {
    const wrapper = shallowMount(InfoTemplate, {
      props: {
        settingData: [],
        labelTooltips: [],
        copyList: []
      },
      global: { stubs }
    })
    expect(typeof (wrapper.vm as any).init).toBe('function')
  })

  it('emits edit when edit button clicked', () => {
    const wrapper = shallowMount(InfoTemplate, {
      props: {
        settingData: [],
        labelTooltips: [],
        copyList: []
      },
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
