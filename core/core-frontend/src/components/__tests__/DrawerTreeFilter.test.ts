import { defineComponent, nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => `t:${key}`
  })
}))

import DrawerTreeFilter from '../drawer-filter/src/DrawerTreeFilter.vue'

const flattenNodes = (nodes: Array<Record<string, any>>): Array<Record<string, any>> =>
  nodes.flatMap(node => [node, ...(node.children ? flattenNodes(node.children) : [])])

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
      default: false
    },
    checkStrictly: {
      type: Boolean,
      default: false
    },
    checkOnClickNode: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue'],
  setup(props, { expose }) {
    expose({
      getNode(id: string) {
        const node = flattenNodes(props.data).find(item => item.value === id)
        return { data: node }
      }
    })

    return {}
  },
  template:
    '<div class="el-tree-select-stub" :data-count="String(modelValue.length)" :data-placeholder="placeholder" :data-show-checkbox="String(showCheckbox)" :data-check-strictly="String(checkStrictly)" :data-check-on-click-node="String(checkOnClickNode)"></div>'
})

const mountComponent = (props?: Record<string, unknown>) =>
  mount(DrawerTreeFilter, {
    props: {
      optionList: [
        {
          value: 'team',
          label: 'Team',
          children: [{ value: 'east', label: 'East Team' }]
        }
      ],
      title: 'Tree Filter',
      ...props
    },
    global: {
      stubs: {
        ElTreeSelect: ElTreeSelectStub
      },
      mocks: {
        $t: (key: string) => `t:${key}`
      }
    }
  })

describe('DrawerTreeFilter', () => {
  it('renders the title and merged placeholder configuration', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('Tree Filter')
    expect(wrapper.get('.el-tree-select-stub').attributes('data-placeholder')).toBe(
      't:common.please_selectt:user.role'
    )
    expect(wrapper.get('.el-tree-select-stub').attributes('data-show-checkbox')).toBe('true')
  })

  it('emits selected tree values when the selection changes', async () => {
    const wrapper = mountComponent()

    wrapper.getComponent(ElTreeSelectStub).vm.$emit('update:modelValue', ['team', 'east'])
    await nextTick()

    expect(wrapper.emitted('filter-change')?.at(-1)).toEqual([['team', 'east']])
  })

  it('clears the active tree selection through the exposed API', async () => {
    const wrapper = mountComponent()

    wrapper.getComponent(ElTreeSelectStub).vm.$emit('update:modelValue', ['team'])
    await nextTick()
    ;(wrapper.vm as unknown as { clear: () => void }).clear()
    await nextTick()

    expect(wrapper.get('.el-tree-select-stub').attributes('data-count')).toBe('0')
    expect(wrapper.emitted('filter-change')?.at(-1)).toEqual([[]])
  })
})
