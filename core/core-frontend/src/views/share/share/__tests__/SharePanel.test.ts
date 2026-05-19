import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

import SharePanel from '../SharePanel.vue'

describe('SharePanel', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(SharePanel)
    expect(wrapper.exists()).toBe(true)
  })

  it('emits loaded event on mount with panel info', () => {
    const wrapper = shallowMount(SharePanel)
    const emitted = wrapper.emitted('loaded')
    expect(emitted).toBeTruthy()
    expect(emitted![0][0]).toEqual({
      title: 'visualization.share_out',
      name: 'share'
    })
  })

  it('panel info contains correct name property', () => {
    const wrapper = shallowMount(SharePanel)
    const emitted = wrapper.emitted('loaded')
    const panelInfo = emitted![0][0] as { title: string; name: string }
    expect(panelInfo.name).toBe('share')
  })
})
