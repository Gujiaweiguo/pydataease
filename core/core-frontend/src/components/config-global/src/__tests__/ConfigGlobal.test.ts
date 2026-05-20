import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

vi.mock('@/store/modules/locale', () => ({
  useLocaleStore: () => ({
    currentLocale: { elLocale: { name: 'en' } }
  })
}))

import ConfigGlobal from '../ConfigGlobal.vue'

describe('ConfigGlobal', () => {
  it('should render without errors', () => {
    const wrapper = shallowMount(ConfigGlobal, {
      global: {
        stubs: {
          ElConfigProvider: {
            template: '<div class="config-provider-stub"><slot /></div>',
            props: ['locale', 'namespace']
          }
        }
      }
    })
    expect(wrapper.find('.config-provider-stub').exists()).toBe(true)
  })

  it('should render slot content', () => {
    const wrapper = shallowMount(ConfigGlobal, {
      slots: {
        default: '<span class="child-content">child</span>'
      },
      global: {
        stubs: {
          ElConfigProvider: {
            template: '<div class="config-provider-stub"><slot /></div>',
            props: ['locale', 'namespace']
          }
        }
      }
    })
    expect(wrapper.find('.child-content').exists()).toBe(true)
  })
})
