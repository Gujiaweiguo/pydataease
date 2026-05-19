import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import ErrorTemplate from '@/views/share/link/ErrorTemplate.vue'

const EmptyBackgroundStub = defineComponent({
  name: 'EmptyBackground',
  props: {
    imgType: {
      type: String,
      default: ''
    },
    description: {
      type: String,
      default: ''
    }
  },
  template: '<div class="empty-background-stub" :data-img-type="imgType">{{ description }}</div>'
})

describe('ErrorTemplate', () => {
  it('passes the provided message to EmptyBackground', () => {
    const wrapper = mount(ErrorTemplate, {
      props: { msg: '链接已失效' },
      global: { stubs: { EmptyBackground: EmptyBackgroundStub } }
    })

    expect(wrapper.get('.empty-background-stub').text()).toContain('链接已失效')
  })

  it('uses the noneWhite empty background image type', () => {
    const wrapper = mount(ErrorTemplate, {
      props: { msg: '无权限访问' },
      global: { stubs: { EmptyBackground: EmptyBackgroundStub } }
    })

    expect(wrapper.get('.empty-background-stub').attributes('data-img-type')).toBe('noneWhite')
  })

  it('renders an empty description by default', () => {
    const wrapper = mount(ErrorTemplate, {
      global: { stubs: { EmptyBackground: EmptyBackgroundStub } }
    })

    expect(wrapper.get('.empty-background-stub').text()).toBe('')
  })

  it('updates the forwarded description when props change', async () => {
    const wrapper = mount(ErrorTemplate, {
      props: { msg: '初始消息' },
      global: { stubs: { EmptyBackground: EmptyBackgroundStub } }
    })

    await wrapper.setProps({ msg: '更新后的消息' })

    expect(wrapper.get('.empty-background-stub').text()).toContain('更新后的消息')
  })
})
