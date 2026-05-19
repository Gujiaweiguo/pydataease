import { defineComponent, nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import ColumnList from '../column-list/src/ColumnList.vue'

const ElDropdownStub = defineComponent({
  name: 'ElDropdown',
  template: '<div class="dropdown-stub"><slot /><slot name="dropdown" /></div>'
})

const ElDropdownMenuStub = defineComponent({
  name: 'ElDropdownMenu',
  template: '<div class="dropdown-menu-stub"><slot /></div>'
})

const ElCheckboxStub = defineComponent({
  name: 'ElCheckbox',
  props: {
    modelValue: {
      type: Boolean,
      default: undefined
    },
    label: {
      type: String,
      default: ''
    },
    indeterminate: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'change'],
  template:
    '<label class="checkbox-stub" :data-label="label" :data-indeterminate="String(indeterminate)"><slot /></label>'
})

const ElCheckboxGroupStub = defineComponent({
  name: 'ElCheckboxGroup',
  props: {
    modelValue: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:modelValue', 'change'],
  template: '<div class="checkbox-group-stub"><slot /></div>'
})

describe('ColumnList', () => {
  const columnNames = [
    { label: 'component.name', props: 'name' },
    { label: 'component.dept', props: 'dept' },
    { label: 'component.roles', props: 'roles' }
  ]

  const mountComponent = (isPluginLoaded = false) =>
    mount(ColumnList, {
      props: {
        columnNames,
        isPluginLoaded
      },
      global: {
        mocks: {
          $t: (key: string) => `translated:${key}`
        },
        stubs: {
          ElDropdown: ElDropdownStub,
          ElDropdownMenu: ElDropdownMenuStub,
          ElCheckbox: ElCheckboxStub,
          ElCheckboxGroup: ElCheckboxGroupStub,
          ElButton: {
            template: '<button class="button-stub"><slot name="icon" /><slot /></button>'
          },
          ElIcon: {
            template: '<i class="icon-stub"><slot /></i>'
          },
          ElMain: {
            template: '<div class="main-stub"><slot /></div>'
          },
          Icon: {
            template: '<span class="custom-icon-stub"><slot /></span>'
          }
        }
      }
    })

  it('renders the translated title and column labels', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('translated:component.columnList')
    expect(wrapper.text()).toContain('translated:component.selectInfo')
    expect(wrapper.text()).toContain('translated:component.name')
    expect(wrapper.text()).toContain('translated:component.dept')
    expect(wrapper.text()).toContain('translated:component.roles')
  })

  it('emits all columns when check-all is enabled for loaded plugins', async () => {
    const wrapper = mountComponent(true)
    const checkAll = wrapper.findAllComponents(ElCheckboxStub)[0]

    checkAll.vm.$emit('update:modelValue', true)
    checkAll.vm.$emit('change', true)
    await nextTick()

    expect(wrapper.emitted('columnChange')).toEqual([[['name', 'dept', 'roles']]])
  })

  it('filters plugin-only columns when check-all runs without plugin support', async () => {
    const wrapper = mountComponent(false)
    const checkAll = wrapper.findAllComponents(ElCheckboxStub)[0]

    checkAll.vm.$emit('update:modelValue', true)
    checkAll.vm.$emit('change', true)
    await nextTick()

    expect(wrapper.emitted('columnChange')).toEqual([[['name']]])
  })

  it('marks the selection as indeterminate and emits the selected columns', async () => {
    const wrapper = mountComponent(true)
    const group = wrapper.findComponent(ElCheckboxGroupStub)

    group.vm.$emit('update:modelValue', ['name'])
    group.vm.$emit('change', ['name'])
    await nextTick()

    expect(wrapper.emitted('columnChange')).toEqual([[['name']]])
    expect(wrapper.findAllComponents(ElCheckboxStub)[0].attributes('data-indeterminate')).toBe('true')
  })
})
