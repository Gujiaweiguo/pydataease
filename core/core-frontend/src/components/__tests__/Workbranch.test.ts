import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/assets/svg/icon_dashboard.svg', () => ({
  default: {
    name: 'IconDashboard',
    template: '<svg class="dashboard-icon"></svg>'
  }
}))

import Workbranch from '@/views/mobile/components/Workbranch.vue'

const IconStub = defineComponent({
  name: 'Icon',
  template: '<span class="icon-stub"><slot /></span>'
})

const ElIconStub = defineComponent({
  name: 'ElIcon',
  template: '<i class="el-icon-stub"><slot /></i>'
})

const mountWorkbranch = (props = {}) =>
  mount(Workbranch, {
    props,
    global: {
      stubs: {
        Icon: IconStub,
        ElIcon: ElIconStub
      }
    }
  })

describe('Workbranch', () => {
  it('renders the label and timestamp text', () => {
    const wrapper = mountWorkbranch({ label: '市场大盘', time: '2026-05-19 10:00' })

    expect(wrapper.text()).toContain('市场大盘')
    expect(wrapper.text()).toContain('2026-05-19 10:00')
  })

  it('renders the dashboard icon', () => {
    const wrapper = mountWorkbranch({ label: '看板', time: '刚刚' })

    expect(wrapper.find('.dashboard-icon').exists()).toBe(true)
  })

  it('supports empty default props', () => {
    const wrapper = mountWorkbranch()

    expect(wrapper.get('.text').text()).toBe('')
    expect(wrapper.get('.time').text()).toBe('')
  })

  it('emits click when the card is clicked', async () => {
    const wrapper = mountWorkbranch({ label: '点击项' })

    await wrapper.get('.workbranch-cell').trigger('click')

    expect(wrapper.emitted('click')).toEqual([[]])
  })
})
