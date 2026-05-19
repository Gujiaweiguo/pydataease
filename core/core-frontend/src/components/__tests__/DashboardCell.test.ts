import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/assets/svg/icon_right_outlined.svg', () => ({
  default: {
    name: 'IconRightOutlined',
    template: '<svg class="right-icon"></svg>'
  }
}))

import DashboardCell from '@/views/mobile/components/DashboardCell.vue'

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

const mountDashboardCell = (props = {}) =>
  mount(DashboardCell, {
    props,
    global: {
      stubs: {
        Icon: IconStub,
        ElIcon: ElIconStub
      }
    }
  })

describe('DashboardCell', () => {
  it('renders the label and prefix icon', () => {
    const wrapper = mountDashboardCell({ label: '销售看板', prefixIcon: PrefixIcon })

    expect(wrapper.text()).toContain('销售看板')
    expect(wrapper.find('.prefix-icon').exists()).toBe(true)
  })

  it('does not render the next-level arrow by default', () => {
    const wrapper = mountDashboardCell({ label: '概览' })

    expect(wrapper.find('.switch').exists()).toBe(false)
    expect(wrapper.find('.right-icon').exists()).toBe(false)
  })

  it('renders the next-level arrow when nextlevel is enabled', () => {
    const wrapper = mountDashboardCell({ label: '组织详情', nextlevel: true })

    expect(wrapper.find('.switch').exists()).toBe(true)
    expect(wrapper.find('.right-icon').exists()).toBe(true)
  })

  it('emits click when the cell is clicked', async () => {
    const wrapper = mountDashboardCell({ label: '点击我' })

    await wrapper.get('.dashboard-cell').trigger('click')

    expect(wrapper.emitted('click')).toEqual([[]])
  })
})
