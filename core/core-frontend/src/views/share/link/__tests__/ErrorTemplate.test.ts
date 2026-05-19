import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

import ErrorTemplate from '../ErrorTemplate.vue'

const globalStubs = {
  EmptyBackground: {
    template: '<div class="empty-bg">{{ description }}</div>',
    props: ['imgType', 'description']
  }
}

describe('ErrorTemplate', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(ErrorTemplate, {
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders EmptyBackground with msg text', () => {
    const wrapper = shallowMount(ErrorTemplate, {
      props: { msg: 'Something went wrong' },
      global: { stubs: globalStubs }
    })
    expect(wrapper.text()).toContain('Something went wrong')
  })

  it('renders EmptyBackground with default empty msg', () => {
    const wrapper = shallowMount(ErrorTemplate, {
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.empty-bg').exists()).toBe(true)
  })
})
