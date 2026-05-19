import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/config/axios', () => ({}))

import OnlineMapGaode from '../OnlineMapGaode.vue'

describe('OnlineMapGaode', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(OnlineMapGaode, {
      props: { mapKey: '' }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders map container div', () => {
    const wrapper = shallowMount(OnlineMapGaode, {
      props: { mapKey: '' }
    })
    expect(wrapper.find('.de-map-container').exists()).toBe(true)
  })

  it('does not attempt to load map when mapKey is empty', () => {
    const wrapper = shallowMount(OnlineMapGaode, {
      props: { mapKey: '' }
    })
    expect((wrapper.vm as any).mapInstance).toBeNull()
  })
})
