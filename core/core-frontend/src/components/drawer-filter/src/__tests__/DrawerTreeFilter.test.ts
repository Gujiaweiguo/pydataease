import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => `translated:${key}`
  })
}))

import DrawerTreeFilter from '../DrawerTreeFilter.vue'

const ElTreeSelectStub = defineComponent({
  name: 'ElTreeSelect',
  props: {
    modelValue: {
      type: Array,
      default: () => []
    },
    data: {
      type: Array,
      default: () => []
    },
    placeholder: {
      type: String,
      default: ''
    },
    showCheckbox: {
      type: Boolean,
      default: true
    },
    checkStrictly: {
      type: Boolean,
      default: false
    },
    checkOnClickNode: {
      type: Boolean,
      default: true
    }
  },
  template: '<div class="tree-select-stub" :data-placeholder="placeholder"><slot /></div>'
})

const mountComponent = () =>
  mount(DrawerTreeFilter, {
    props: {
      optionList: [
        { value: 'admin', label: 'Admin', children: [] },
        { value: 'user', label: 'User', children: [] }
      ],
      title: 'Role Filter',
      property: {
        checkStrictly: false,
        showCheckbox: true,
        checkOnClickNode: true,
        placeholder: 'roles'
      }
    },
    global: {
      stubs: {
        ElTreeSelect: ElTreeSelectStub
      },
      mocks: {
        $t: (key: string) => `translated:${key}`
      }
    }
  })

describe('DrawerTreeFilter', () => {
  it('renders the title', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('Role Filter')
  })

  it('renders tree select with placeholder', () => {
    const wrapper = mountComponent()

    expect(wrapper.find('.tree-select-stub').exists()).toBe(true)
  })

  it('exposes clear method', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as unknown as { clear: () => void }

    expect(typeof vm.clear).toBe('function')
  })
})
