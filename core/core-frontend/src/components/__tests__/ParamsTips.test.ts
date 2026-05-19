import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => key
  })
}))

import ParamsTips from '@/views/watermark/ParamsTips.vue'

const ElTooltipStub = defineComponent({
  name: 'ElTooltip',
  props: {
    effect: {
      type: String,
      default: ''
    },
    placement: {
      type: String,
      default: ''
    }
  },
  template:
    '<div class="tooltip-stub" :data-effect="effect" :data-placement="placement"><div class="tooltip-content"><slot name="content" /></div><div class="tooltip-trigger"><slot /></div></div>'
})

const ElIconStub = defineComponent({
  name: 'ElIcon',
  template: '<i class="el-icon-stub"><slot /></i>'
})

const InfoFilledStub = defineComponent({
  name: 'InfoFilled',
  template: '<svg class="info-filled-stub"></svg>'
})

describe('ParamsTips', () => {
  it('renders the translated support heading and account placeholders', () => {
    const wrapper = mount(ParamsTips, {
      global: {
        stubs: {
          ElTooltip: ElTooltipStub,
          ElIcon: ElIconStub,
          InfoFilled: InfoFilledStub
        }
      }
    })

    expect(wrapper.text()).toContain('watermark.support_params')
    expect(wrapper.text()).toContain('${username}-watermark.account')
    expect(wrapper.text()).toContain('${nickName}-watermark.nick_name')
  })

  it('shows all supported dynamic placeholders inside the tooltip content', () => {
    const wrapper = mount(ParamsTips, {
      global: {
        stubs: {
          ElTooltip: ElTooltipStub,
          ElIcon: ElIconStub,
          InfoFilled: InfoFilledStub
        }
      }
    })

    expect(wrapper.text()).toContain('${time}-watermark.now')
    expect(wrapper.text()).toContain('${ip}-IP')
    expect(wrapper.find('.tooltip-content').exists()).toBe(true)
  })

  it('passes tooltip configuration and renders the info icon trigger', () => {
    const wrapper = mount(ParamsTips, {
      global: {
        stubs: {
          ElTooltip: ElTooltipStub,
          ElIcon: ElIconStub,
          InfoFilled: InfoFilledStub
        }
      }
    })

    expect(wrapper.get('.tooltip-stub').attributes('data-effect')).toBe('dark')
    expect(wrapper.get('.tooltip-stub').attributes('data-placement')).toBe('bottom')
    expect(wrapper.find('.info-filled-stub').exists()).toBe(true)
  })
})
