import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/assets/svg/icon_right_outlined.svg', () => ({
  default: {
    name: 'IconRightOutlined',
    template: '<svg class="right-icon"></svg>'
  }
}))

import OrgCell from '@/views/mobile/components/OrgCell.vue'

const IconStub = defineComponent({
  name: 'Icon',
  template: '<span class="icon-stub"><slot /></span>'
})

const ElIconStub = defineComponent({
  name: 'ElIcon',
  template: '<i class="el-icon-stub"><slot /></i>'
})

const PrefixIcon = defineComponent({
  name: 'PrefixIcon',
  template: '<svg class="prefix-icon"></svg>'
})

const mountOrgCell = (props = {}) =>
  mount(OrgCell, {
    props,
    global: {
      stubs: {
        Icon: IconStub,
        ElIcon: ElIconStub
      }
    }
  })

describe('OrgCell', () => {
  it('renders the label, prefix icon and active style', () => {
    const wrapper = mountOrgCell({
      label: '研发中心',
      active: true,
      prefixIcon: PrefixIcon
    })

    expect(wrapper.text()).toContain('研发中心')
    expect(wrapper.find('.prefix-icon').exists()).toBe(true)
    expect(wrapper.get('.label').classes()).toContain('active')
  })

  it('emits all-area clicks from both hit areas when nextlevel is disabled', async () => {
    const wrapper = mountOrgCell({
      label: '所有组织'
    })

    expect(wrapper.find('.switch').exists()).toBe(false)

    await wrapper.get('.left-area').trigger('click')
    await wrapper.get('.right-area').trigger('click')

    expect(wrapper.emitted('click')).toEqual([['all'], ['all']])
  })

  it('renders switch tips and differentiates left/right clicks when nextlevel is enabled', async () => {
    const wrapper = mountOrgCell({
      label: '华东大区',
      nextlevel: true,
      tips: '3个子组织'
    })

    expect(wrapper.get('.switch').text()).toContain('3个子组织')
    expect(wrapper.find('.right-icon').exists()).toBe(true)

    await wrapper.get('.left-area').trigger('click')
    await wrapper.get('.right-area').trigger('click')

    expect(wrapper.emitted('click')).toEqual([['left'], ['right']])
  })
})
