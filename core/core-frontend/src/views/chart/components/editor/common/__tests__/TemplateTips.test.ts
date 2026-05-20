import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

import TemplateTips from '../TemplateTips.vue'

describe('TemplateTips', () => {
  it('renders component', () => {
    const wrapper = shallowMount(TemplateTips, {
      global: {
        stubs: {
          'el-popover': { template: '<div><slot /><slot name="reference" /></div>' },
          'el-icon': { template: '<div><slot /></div>' },
          Icon: { template: '<div><slot /></div>' },
          dvAi: true
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains ai-popper-tips-icon element', () => {
    const wrapper = shallowMount(TemplateTips, {
      global: {
        stubs: {
          'el-popover': { template: '<div><slot /><slot name="reference" /></div>' },
          'el-icon': { template: '<div><slot /></div>' },
          Icon: { template: '<div><slot /></div>' },
          dvAi: true
        }
      }
    })
    expect(wrapper.find('.ai-popper-tips-icon').exists()).toBe(true)
  })
})
