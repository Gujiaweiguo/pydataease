import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

import ChartTemplateInfo from '../ChartTemplateInfo.vue'

describe('ChartTemplateInfo', () => {
  it('renders component', () => {
    const wrapper = shallowMount(ChartTemplateInfo, {
      props: { themes: 'light' },
      global: {
        stubs: {
          'el-popover': { template: '<div><slot /><slot name="reference" /></div>' }
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains view-panel-mask-left element', () => {
    const wrapper = shallowMount(ChartTemplateInfo, {
      props: { themes: 'light' },
      global: {
        stubs: {
          'el-popover': { template: '<div><slot /><slot name="reference" /></div>' }
        }
      }
    })
    expect(wrapper.find('.view-panel-mask-left').exists()).toBe(true)
  })

  it('contains view-panel-mask element', () => {
    const wrapper = shallowMount(ChartTemplateInfo, {
      props: { themes: 'light' },
      global: {
        stubs: {
          'el-popover': { template: '<div><slot /><slot name="reference" /></div>' }
        }
      }
    })
    expect(wrapper.find('.view-panel-mask').exists()).toBe(true)
  })
})
