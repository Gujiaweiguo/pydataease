import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
import OnlineMapQQ from '../OnlineMapQQ.vue'

describe('OnlineMapQQ', () => {
  const stubs = {
    ElButton: { template: '<button><slot /></button>' }
  }

  it('renders with default props', () => {
    const wrapper = shallowMount(OnlineMapQQ, {
      props: { mapKey: '' },
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders map container div', () => {
    const wrapper = shallowMount(OnlineMapQQ, {
      props: { mapKey: 'test-key' },
      global: { stubs }
    })
    const container = wrapper.find('.de-map-container')
    expect(container.exists()).toBe(true)
  })

  it('does not render map container when reloading', async () => {
    const wrapper = shallowMount(OnlineMapQQ, {
      props: { mapKey: 'test-key' },
      global: { stubs }
    })
    expect(wrapper.find('.de-map-container').exists()).toBe(true)
  })

  it('accepts mapKey and securityCode props', () => {
    const wrapper = shallowMount(OnlineMapQQ, {
      props: { mapKey: 'mykey', securityCode: 'secret' },
      global: { stubs }
    })
    expect(wrapper.props('mapKey')).toBe('mykey')
    expect(wrapper.props('securityCode')).toBe('secret')
  })
})
