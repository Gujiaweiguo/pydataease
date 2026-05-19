import { nextTick } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

const { multFieldValuesForPermissionsMock } = vi.hoisted(() => ({
  multFieldValuesForPermissionsMock: vi.fn().mockResolvedValue({ data: ['A', '', 'B'] })
}))

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (key: string) => key }) }))

vi.mock('@/api/dataset', () => ({
  multFieldValuesForPermissions: multFieldValuesForPermissionsMock
}))

import ResultFilterEditor from '../ResultFilterEditor.vue'

const flushPromises = async () => {
  await Promise.resolve()
  await nextTick()
}

const globalStubs = {
  ElCol: { template: '<div class="col-stub"><slot /></div>' },
  ElSelect: { props: ['modelValue'], template: '<select class="select-stub"><slot /></select>' },
  ElOption: {
    props: ['label', 'value'],
    template: '<option class="option-stub" :value="value">{{ label }}</option>'
  },
  ElOptionGroup: {
    props: ['label'],
    template: '<optgroup class="option-group-stub"><slot /></optgroup>'
  },
  ElInput: { props: ['modelValue'], template: '<input class="input-stub" />' },
  ElButton: { template: '<button class="button-stub"><slot /></button>' },
  ElRadioGroup: { props: ['modelValue'], template: '<div class="radio-group-stub"><slot /></div>' },
  ElRadio: {
    props: ['value'],
    template: '<label class="radio-stub" :data-value="value"><slot /></label>'
  },
  ElIcon: { template: '<i class="icon-stub"><slot /></i>' },
  Icon: { template: '<span class="vant-icon-stub"><slot /></span>' }
}

const createItem = (overrides: Record<string, unknown> = {}) => ({
  id: 'field-1',
  name: 'Category',
  deType: 0,
  logic: 'and',
  filterType: 'logic',
  enumCheckField: [],
  filter: [{ fieldId: 'field-1', term: 'eq', value: 'A' }],
  ...overrides
})

const mountComponent = (item = createItem()) =>
  shallowMount(ResultFilterEditor, {
    props: {
      chart: { id: 'chart-1' },
      item
    },
    global: {
      stubs: globalStubs
    }
  })

describe('ResultFilterEditor', () => {
  it('initializes text filter options for string fields', () => {
    const wrapper = mountComponent()
    const optionValues = (wrapper.vm as any).state.options.flatMap(group =>
      group.options.map(option => option.value)
    )

    expect(optionValues).toContain('like')
    expect(optionValues).toContain('empty')
    expect((wrapper.vm as any).state.filterType).toBe('logic')
  })

  it('loads enum options once and maps them into field options', async () => {
    const wrapper = mountComponent()

    ;(wrapper.vm as any).filterTypeChange('enum')
    await flushPromises()

    expect(multFieldValuesForPermissionsMock).toHaveBeenCalledWith({ fieldIds: ['field-1'] })
    expect((wrapper.vm as any).state.fieldOptions).toEqual([
      { id: 'A', text: 'A' },
      { id: 'B', text: 'B' }
    ])
  })

  it('adds filters with the current field id and updates the item logic', () => {
    const item = createItem()
    const wrapper = mountComponent(item)

    ;(wrapper.vm as any).addFilter()
    ;(wrapper.vm as any).logicChange('or')

    expect(item.filter[item.filter.length - 1]).toEqual({
      fieldId: 'field-1',
      term: 'eq',
      value: ''
    })
    expect(item.logic).toBe('or')
  })

  it('syncs enum selections back to the item model', () => {
    const item = createItem({ filterType: 'enum' })
    const wrapper = mountComponent(item)
    const vm = wrapper.vm as any

    vm.state.enumCheckField = ['A', 'B']
    vm.enumChange()

    expect(item.enumCheckField).toEqual(['A', 'B'])
  })
})
