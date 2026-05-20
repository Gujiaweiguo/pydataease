import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

import RowAuth from '../RowAuth.vue'

describe('RowAuth (auth-tree)', () => {
  it('renders component', () => {
    const wrapper = shallowMount(RowAuth, {
      global: {
        stubs: {
          'auth-tree': true
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains rowAuth wrapper', () => {
    const wrapper = shallowMount(RowAuth, {
      global: {
        stubs: {
          'auth-tree': true
        }
      }
    })
    expect(wrapper.find('.rowAuth').exists()).toBe(true)
  })

  it('renders svg elements for connection lines', () => {
    const wrapper = shallowMount(RowAuth, {
      global: {
        stubs: {
          'auth-tree': true
        }
      }
    })
    expect(wrapper.find('svg.real-line').exists()).toBe(true)
    expect(wrapper.find('svg.dash-line').exists()).toBe(true)
  })
})
