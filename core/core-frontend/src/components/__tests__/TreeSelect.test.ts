import { defineComponent } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import TreeSelect from '../tree-select/src/TreeSelect.vue'

const ElTreeSelectStub = defineComponent({
  name: 'ElTreeSelect',
  props: {
    load: {
      type: Function,
      required: true
    },
    filterNodeMethod: {
      type: Function,
      required: true
    },
    props: {
      type: Object,
      default: () => ({})
    },
    lazy: {
      type: Boolean,
      default: false
    },
    filterable: {
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
    },
    expandOnClickNode: {
      type: Boolean,
      default: true
    }
  },
  template: '<div class="el-tree-select-stub"></div>'
})

const mountComponent = () =>
  shallowMount(TreeSelect, {
    global: {
      stubs: {
        ElTreeSelect: ElTreeSelectStub
      }
    }
  })

describe('TreeSelect', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  it('passes lazy loading and default tree props to the tree select', () => {
    const wrapper = mountComponent()
    const tree = wrapper.getComponent(ElTreeSelectStub)

    expect(tree.props('lazy')).toBe(true)
    expect(tree.props('filterable')).toBe(true)
    expect(tree.props('checkStrictly')).toBe(true)
    expect(tree.props('checkOnClickNode')).toBe(true)
    expect(tree.props('expandOnClickNode')).toBe(false)
    expect(tree.props('props')).toMatchObject({
      children: 'children',
      label: 'name'
    })
  })

  it('filters tree nodes by matching the entered name', () => {
    const wrapper = mountComponent()
    const filterNodeMethod = wrapper
      .getComponent(ElTreeSelectStub)
      .props('filterNodeMethod') as (query: string, data: Record<string, unknown>) => boolean

    expect(filterNodeMethod('wei', { name: 'wei的组织' })).toBe(true)
    expect(filterNodeMethod('sales', { name: 'wei的组织' })).toBe(false)
  })

  it('loads root nodes lazily and resolves top-level organizations', () => {
    vi.useFakeTimers()
    const wrapper = mountComponent()
    const loadNode = wrapper.getComponent(ElTreeSelectStub).props('load') as (node: { level: number }, resolve: (data: unknown[]) => void) => void
    const resolve = vi.fn()

    loadNode({ level: 0 }, resolve)
    vi.advanceTimersByTime(500)

    expect(resolve).toHaveBeenCalledWith(
      expect.arrayContaining([
        expect.objectContaining({ value: 2, name: 'wei的组织', hasChildren: true }),
        expect.objectContaining({ value: 5, name: 'jinlong', leaf: true })
      ])
    )
  })

  it('stops loading once the node depth is beyond the supported level', () => {
    const wrapper = mountComponent()
    const loadNode = wrapper.getComponent(ElTreeSelectStub).props('load') as (node: { level: number }, resolve: (data: unknown[]) => void) => void
    const resolve = vi.fn()

    loadNode({ level: 2 }, resolve)

    expect(resolve).toHaveBeenCalledWith([])
  })
})
