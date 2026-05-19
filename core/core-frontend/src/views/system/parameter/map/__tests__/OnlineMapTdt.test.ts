import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
import OnlineMapTdt from '../OnlineMapTdt.vue'

describe('OnlineMapTdt', () => {
  const stubs = {
    ElButton: { template: '<button><slot /></button>' }
  }

  it('renders with default props', () => {
    const wrapper = shallowMount(OnlineMapTdt, {
      props: { mapKey: '' },
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders map container div', () => {
    const wrapper = shallowMount(OnlineMapTdt, {
      props: { mapKey: 'test-key' },
      global: { stubs }
    })
    const container = wrapper.find('.de-map-container')
    expect(container.exists()).toBe(true)
  })

  it('accepts mapKey and securityCode props', () => {
    const wrapper = shallowMount(OnlineMapTdt, {
      props: { mapKey: 'tdt-key', securityCode: 'tdt-secret' },
      global: { stubs }
    })
    expect(wrapper.props('mapKey')).toBe('tdt-key')
    expect(wrapper.props('securityCode')).toBe('tdt-secret')
  })

  it('has correct domId ref', () => {
    const wrapper = shallowMount(OnlineMapTdt, {
      props: { mapKey: '' },
      global: { stubs }
    })
    const container = wrapper.find('.de-map-container')
    expect(container.attributes('id')).toBe('de-map-container')
  })
})
