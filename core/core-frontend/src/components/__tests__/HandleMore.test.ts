import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import HandleMore from '../handle-more/src/HandleMore.vue'

const DummyIcon = defineComponent({
  name: 'DummyIcon',
  template: '<svg class="dummy-icon"></svg>'
})

const ElDropdownStub = defineComponent({
  name: 'ElDropdown',
  props: {
    placement: {
      type: String,
      default: ''
    },
    persistent: {
      type: Boolean,
      default: true
    },
    trigger: {
      type: String,
      default: ''
    }
  },
  template:
    '<div class="dropdown-stub" :data-placement="placement" :data-persistent="String(persistent)" :data-trigger="trigger"><slot /><div class="dropdown-content"><slot name="dropdown" /></div></div>'
})

const ElDropdownMenuStub = defineComponent({
  name: 'ElDropdownMenu',
  template: '<div class="dropdown-menu-stub"><slot /></div>'
})

const ElDropdownItemStub = defineComponent({
  name: 'ElDropdownItem',
  props: {
    command: {
      type: [String, Number, Object],
      default: ''
    },
    disabled: {
      type: Boolean,
      default: false
    },
    divided: {
      type: Boolean,
      default: false
    }
  },
  template:
    '<div class="dropdown-item-stub" :data-command="String(command)" :data-disabled="String(disabled)" :data-divided="String(divided)"><slot /></div>'
})

const ElIconStub = defineComponent({
  name: 'ElIcon',
  template: '<div class="el-icon-stub" :class="$attrs.class"><slot /></div>'
})

const mountComponent = (props: Record<string, unknown>) =>
  mount(HandleMore, {
    props,
    global: {
      stubs: {
        ElDropdown: ElDropdownStub,
        ElDropdownMenu: ElDropdownMenuStub,
        ElDropdownItem: ElDropdownItemStub,
        ElIcon: ElIconStub,
        Icon: {
          template: '<span class="icon-stub"><slot /></span>'
        }
      }
    }
  })

describe('HandleMore', () => {
  it('renders menu items with the default placement', () => {
    const wrapper = mountComponent({
      menuList: [
        { label: 'Edit', command: 'edit' },
        { label: 'Delete', command: 'delete', disabled: true }
      ]
    })

    expect(wrapper.get('.dropdown-stub').attributes('data-placement')).toBe('bottom-end')
    expect(wrapper.findAll('.dropdown-item-stub')).toHaveLength(2)
    expect(wrapper.text()).toContain('Edit')
    expect(wrapper.text()).toContain('Delete')
  })

  it('applies table styling and custom icon size props', () => {
    const wrapper = mountComponent({
      inTable: true,
      iconSize: '24px',
      placement: 'top',
      menuList: [{ label: 'Share', command: 'share', svgName: DummyIcon }]
    })

    expect(wrapper.get('.dropdown-stub').attributes('data-placement')).toBe('top')
    expect(wrapper.get('.hover-icon').classes()).toContain('hover-icon-in-table')
    expect(wrapper.get('.handle-icon').attributes('style')).toContain('font-size: 24px')
    expect(wrapper.find('.dummy-icon').exists()).toBe(true)
  })

  it('emits handleCommand when the dropdown emits a command', async () => {
    const wrapper = mountComponent({
      menuList: [{ label: 'Archive', command: 'archive' }]
    })

    wrapper.getComponent(ElDropdownStub).vm.$emit('command', 'archive')
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('handleCommand')).toEqual([['archive']])
  })
})
