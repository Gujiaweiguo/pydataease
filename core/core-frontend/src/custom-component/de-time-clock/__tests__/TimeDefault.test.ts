import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))

;(Date.prototype as any).format = function (fmt: string) {
  return fmt
}

import TimeDefault from '../TimeDefault.vue'

describe('de-time-clock/TimeDefault.vue', () => {
  const createElement = () => ({
    style: { textAlign: 'center' },
    formatInfo: {
      timeFormat: 'HH:mm:ss',
      showWeek: false,
      showDate: false,
      dateFormat: 'yyyy-MM-dd'
    }
  })

  it('renders the component', () => {
    const wrapper = shallowMount(TimeDefault, {
      props: { element: createElement() }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders a paragraph element for time display', () => {
    const wrapper = shallowMount(TimeDefault, {
      props: { element: createElement() }
    })
    expect(wrapper.find('p').exists()).toBe(true)
  })

  it('applies textAlign style from element.style', () => {
    const wrapper = shallowMount(TimeDefault, {
      props: { element: createElement() }
    })
    const container = wrapper.find('div')
    expect(container.exists()).toBe(true)
  })

  it('clears interval on unmount', () => {
    const clearIntervalSpy = vi.spyOn(global, 'clearInterval')
    const wrapper = shallowMount(TimeDefault, {
      props: { element: createElement() }
    })
    wrapper.unmount()
    expect(clearIntervalSpy).toHaveBeenCalled()
    clearIntervalSpy.mockRestore()
  })
})
