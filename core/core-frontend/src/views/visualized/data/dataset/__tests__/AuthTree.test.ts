import { defineComponent } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => `t:${key}` })
}))

vi.mock('../auth-tree/FilterFiled.vue', () => ({
  default: {
    name: 'FilterFiled',
    props: {
      index: {
        type: Number,
        default: 0
      }
    },
    emits: ['del'],
    template:
      '<button class="filter-filed-stub" type="button" @click="$emit(\'del\')">delete {{ index }}</button>'
  }
}))

import AuthTree from '../auth-tree/AuthTree.vue'

const ElDropdownStub = defineComponent({
  name: 'ElDropdown',
  emits: ['command'],
  template:
    '<div class="dropdown-stub" @click="$emit(\'command\', \'and\')"><slot /><slot name="dropdown" /></div>'
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
  template: '<i class="icon-stub"><slot /></i>'
})

const IconStub = defineComponent({
  name: 'Icon',
  template: '<span class="custom-icon-stub"><slot /></span>'
})

const mountComponent = (props?: Record<string, unknown>) =>
  shallowMount(AuthTree, {
    props,
    global: {
      stubs: {
        ElDropdown: ElDropdownStub,
        ElDropdownItem: ElDropdownItemStub,
        ElDropdownMenu: ElDropdownMenuStub,
        ElIcon: ElIconStub,
        Icon: IconStub
      }
    }
  })

describe('AuthTree', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('emits logic updates from the root dropdown', async () => {
    const wrapper = mountComponent({ relationList: [], logic: 'or', x: 0 })

    await wrapper.get('.dropdown-stub').trigger('click')

    expect(wrapper.emitted('update:logic')).toEqual([['and']])
    expect(wrapper.emitted('changeAndOrDfs')).toEqual([['and']])
  })

  it('emits add-condition and add-relation events with the toggled logic', async () => {
    const wrapper = mountComponent({ relationList: [], logic: 'or', x: 0 })
    const buttons = wrapper.findAll('.operand-btn')

    await buttons[0].trigger('click')
    await buttons[1].trigger('click')

    expect(wrapper.emitted('addCondReal')).toEqual([
      ['condition', 'and'],
      ['relation', 'and']
    ])
  })

  it('emits a remove event for nested relation groups', async () => {
    const relationList = [{ fieldId: '1' }, { fieldId: '2' }] as any[]
    const wrapper = mountComponent({ relationList, logic: 'or', x: 1 })

    await wrapper.get('.operate-icon .icon-stub').trigger('click')

    expect(wrapper.emitted('removeRelationList')).toEqual([[]])
  })

  it('forwards delete events from child filter rows', async () => {
    const wrapper = mountComponent({ relationList: [{ fieldId: '1' }], logic: 'or', x: 0 })

    wrapper.findComponent({ name: 'FilterFiled' }).vm.$emit('del')

    expect(wrapper.emitted('del')).toEqual([[0]])
  })
})
