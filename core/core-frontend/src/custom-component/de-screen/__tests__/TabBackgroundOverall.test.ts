import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/components/visualization/component-background/BackgroundOverallCommon.vue', () => ({
  default: {
    template: '<div class="bg-overall-common-stub" />',
    emits: ['onBackgroundChange']
  }
}))

import TabBackgroundOverall from '../TabBackgroundOverall.vue'

const createElement = () => ({
  titleBackground: {
    enable: false,
    multiply: false,
    active: {
      backgroundColorSelect: false,
      backgroundColor: '#ffffff',
      backgroundImageEnable: false,
      backgroundType: 'innerImage',
      innerPadding: 8,
      borderRadius: 4
    },
    inActive: {
      backgroundColorSelect: false,
      backgroundColor: '#ffffff',
      backgroundImageEnable: false,
      backgroundType: 'innerImage',
      innerPadding: 8,
      borderRadius: 4
    }
  }
})

const mountComponent = (props = {}) =>
  shallowMount(TabBackgroundOverall, {
    props: {
      themes: 'dark',
      element: createElement(),
      ...props
    },
    global: {
      mocks: { $t: (key: string) => key },
      stubs: {
        'el-tabs': { template: '<div class="el-tabs"><slot /></div>' },
        'el-tab-pane': { template: '<div class="el-tab-pane"><slot /></div>' },
        'el-form-item': { template: '<div><slot /></div>' },
        'el-checkbox': { template: '<div><slot /></div>' }
      }
    }
  })

describe('de-screen/TabBackgroundOverall', () => {
  it('renders the root container', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('.tab-title-background').exists()).toBe(true)
  })

  it('accepts themes prop', () => {
    const wrapper = mountComponent({ themes: 'light' })
    expect(wrapper.props('themes')).toBe('light')
  })

  it('accepts element prop', () => {
    const wrapper = mountComponent()
    expect(wrapper.props('element')).toBeDefined()
    expect(wrapper.props('element').titleBackground).toBeDefined()
  })

  it('emits onTitleBackgroundChange when onTitleBackgroundChange is called', async () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any
    vm.onTitleBackgroundChange(null, null)
    await wrapper.vm.$nextTick()
    expect(wrapper.emitted('onTitleBackgroundChange')).toBeTruthy()
  })
})
