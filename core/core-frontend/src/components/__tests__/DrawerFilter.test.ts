import { defineComponent, nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => `translated:${key}`
  })
}))

import DrawerFilter from '../drawer-filter/src/DrawerFilter.vue'

const ElSelectStub = defineComponent({
  name: 'ElSelect',
  props: {
    modelValue: {
      type: Array,
      default: () => []
    },
    placeholder: {
      type: String,
      default: ''
    }
  },
  template:
    '<div class="select-stub" :data-placeholder="placeholder" :data-count="String(modelValue.length)"><slot /></div>'
})

const ElOptionStub = defineComponent({
  name: 'ElOption',
  props: {
    label: {
      type: String,
      default: ''
    },
    value: {
      type: Object,
      default: () => ({})
    }
  },
  template: '<div class="option-stub" :data-label="label">{{ label }}</div>'
})

const mountComponent = () =>
  mount(DrawerFilter, {
    props: {
      optionList: [
        { id: '1', name: 'One' },
        { id: '2', name: 'Fallback', value: 'two' }
      ],
      property: {
        placeholder: ' users'
      },
      title: 'User Filter'
    },
    global: {
      stubs: {
        ElOption: ElOptionStub,
        ElSelect: ElSelectStub
      }
    }
  })

describe('DrawerFilter', () => {
  it('renders the title, options and translated placeholder', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('User Filter')
    expect(wrapper.findAll('.option-stub')).toHaveLength(2)
    expect(wrapper.get('.select-stub').attributes('data-placeholder')).toBe(
      'translated:common.please_select users'
    )
  })

  it('emits selected ids or fallback values on change', async () => {
    const wrapper = mountComponent()
    const selected = [
      { id: '1', name: 'One' },
      { name: 'Fallback', value: 'two' }
    ]

    wrapper.getComponent(ElSelectStub).vm.$emit('update:modelValue', selected)
    wrapper.getComponent(ElSelectStub).vm.$emit('change', selected)
    await nextTick()

    expect(wrapper.emitted('filter-change')).toEqual([[['1', 'two']]])
  })

  it('clears the active selection through the exposed clear method', async () => {
    const wrapper = mountComponent()
    const selected = [{ id: '1', name: 'One' }]

    wrapper.getComponent(ElSelectStub).vm.$emit('update:modelValue', selected)
    await nextTick()
    expect(wrapper.get('.select-stub').attributes('data-count')).toBe('1')
    ;(wrapper.vm as unknown as { clear: () => void }).clear()
    await nextTick()

    expect(wrapper.get('.select-stub').attributes('data-count')).toBe('0')
  })
})
