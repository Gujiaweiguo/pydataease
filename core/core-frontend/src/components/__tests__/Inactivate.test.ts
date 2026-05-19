import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import Inactivate from '@/views/sqlbot/Inactivate.vue'

const ElDropdownStub = defineComponent({
  name: 'ElDropdown',
  emits: ['command'],
  template:
    '<div class="el-dropdown-stub"><button class="show-history" @click="$emit(\'command\', \'showHistory\')">history</button><button class="new-chat" @click="$emit(\'command\', \'newChat\')">new</button><slot /><slot name="dropdown" /></div>'
})

const ElDropdownMenuStub = defineComponent({
  name: 'ElDropdownMenu',
  template: '<div class="dropdown-menu-stub"><slot /></div>'
})

const ElDropdownItemStub = defineComponent({
  name: 'ElDropdownItem',
  template: '<div class="dropdown-item-stub"><slot /></div>'
})

const ElIconStub = defineComponent({
  name: 'ElIcon',
  template: '<i class="el-icon-stub"><slot /></i>'
})

const ArrowDownStub = defineComponent({
  name: 'ArrowDown',
  template: '<svg class="arrow-down-stub"></svg>'
})

const mountInactivate = (props = {}) =>
  mount(Inactivate, {
    props,
    global: {
      stubs: {
        ElDropdown: ElDropdownStub,
        ElDropdownMenu: ElDropdownMenuStub,
        ElDropdownItem: ElDropdownItemStub,
        ElIcon: ElIconStub,
        ArrowDown: ArrowDownStub
      }
    }
  })

describe('Inactivate', () => {
  it('renders the API label and dropdown items', () => {
    const wrapper = mountInactivate()

    expect(wrapper.text()).toContain('API 功能')
    expect(wrapper.text()).toContain('历史记录(显/隐)')
    expect(wrapper.text()).toContain('新建对话')
  })

  it('applies the provided font color style', () => {
    const wrapper = mountInactivate({ fontColor: '#ff0000' })

    expect(wrapper.get('.inactivate-button').attributes('style')).toContain('color: #ff0000;')
  })

  it('emits showHistory for the history command', async () => {
    const wrapper = mountInactivate()

    await wrapper.get('.show-history').trigger('click')

    expect(wrapper.emitted('showHistory')).toEqual([[]])
  })

  it('emits newChat for the new chat command', async () => {
    const wrapper = mountInactivate()

    await wrapper.get('.new-chat').trigger('click')

    expect(wrapper.emitted('newChat')).toEqual([[]])
  })
})
