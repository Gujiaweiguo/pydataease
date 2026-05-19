import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))

import AsideCloseButton from '../AsideCloseButton.vue'

const globalStubs = {
  ElIcon: { template: '<i><slot /></i>' },
  ArrowLeft: { template: '<span>left</span>' },
  ArrowRight: { template: '<span>right</span>' }
}

describe('AsideCloseButton', () => {
  it('renders with slideShow true (shows ArrowLeft)', () => {
    const wrapper = shallowMount(AsideCloseButton, {
      props: { slideShow: true },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.flexible-button-area').exists()).toBe(true)
  })

  it('renders with slideShow false (shows ArrowRight)', () => {
    const wrapper = shallowMount(AsideCloseButton, {
      props: { slideShow: false },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.flexible-button-area').exists()).toBe(true)
  })

  it('emits update:slideShowChange when clicked', async () => {
    const wrapper = shallowMount(AsideCloseButton, {
      props: { slideShow: true },
      global: { stubs: globalStubs }
    })
    await wrapper.find('.flexible-button-area').trigger('click')
    expect(wrapper.emitted('update:slideShowChange')).toBeTruthy()
    expect(wrapper.emitted('update:slideShowChange')![0]).toEqual([false])
  })

  it('emits true when slideShow is false and clicked', async () => {
    const wrapper = shallowMount(AsideCloseButton, {
      props: { slideShow: false },
      global: { stubs: globalStubs }
    })
    await wrapper.find('.flexible-button-area').trigger('click')
    expect(wrapper.emitted('update:slideShowChange')![0]).toEqual([true])
  })
})
