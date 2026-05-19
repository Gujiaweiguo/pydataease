import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('@/assets/svg/dv-ai.svg', () => ({ default: 'dv-ai-svg' }))

import AiTips from '../AiTips.vue'

const globalStubs = {
  ElPopover: {
    template: '<div class="popover-stub"><slot /><slot name="reference" /></div>',
    props: ['visible', 'placement', 'popperClass', 'width', 'showArrow']
  },
  ElButton: { template: '<button class="el-btn-stub"><slot /></button>' },
  ElIcon: { template: '<i><slot /></i>' }
}

describe('AiTips', () => {
  const mountComponent = () =>
    shallowMount(AiTips, {
      global: { stubs: globalStubs }
    })

  it('renders', () => {
    const wrapper = mountComponent()
    expect(wrapper.exists()).toBe(true)
  })

  it('displays AI tips title text', () => {
    const wrapper = mountComponent()
    expect(wrapper.text()).toContain('DataEase')
  })

  it('emits confirm event on button click', async () => {
    const wrapper = mountComponent()
    const btn = wrapper.find('.el-btn-stub')
    await btn.trigger('click')
    expect(wrapper.emitted('confirm')).toBeTruthy()
  })

  it('has popover stub rendered', () => {
    const wrapper = mountComponent()
    expect(wrapper.find('.popover-stub').exists()).toBe(true)
  })
})
