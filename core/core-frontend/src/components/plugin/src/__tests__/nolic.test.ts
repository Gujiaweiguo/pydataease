import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/utils/propTypes', () => ({
  propTypes: {
    bool: {
      def: (val: boolean) => val
    }
  }
}))

import Nolic from '../nolic.vue'

const mountComponent = (errorTips = false) =>
  mount(Nolic, {
    props: {
      errorTips
    }
  })

describe('nolic', () => {
  it('renders empty div when errorTips is false', () => {
    const wrapper = mountComponent(false)

    expect(wrapper.find('div').exists()).toBe(true)
    expect(wrapper.text()).toBe('')
  })

  it('renders license message when errorTips is true', () => {
    const wrapper = mountComponent(true)

    expect(wrapper.text()).toContain('当前不是企业版')
  })
})
