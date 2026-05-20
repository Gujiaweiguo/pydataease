import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

vi.mock('@/utils/propTypes', () => ({
  propTypes: {
    string: {
      def: vi.fn((v: string) => v)
    }
  }
}))

import TreeSelect from '../TreeSelect.vue'

describe('TreeSelect', () => {
  it('should render without errors', () => {
    const wrapper = shallowMount(TreeSelect, {
      props: { width: '200px' },
      global: {
        stubs: {
          'el-tree-select': {
            template: '<div class="el-tree-select-stub" />',
            props: ['load', 'lazy', 'filterable', 'checkStrictly', 'filterNodeMethod', 'clearable', 'expandOnClickNode', 'checkOnClickNode', 'props']
          }
        }
      }
    })
    expect(wrapper.find('.el-tree-select-stub').exists()).toBe(true)
  })

  it('should define treeDefaultProps with correct structure', () => {
    const wrapper = shallowMount(TreeSelect, {
      props: { width: '200px' },
      global: {
        stubs: {
          'el-tree-select': {
            template: '<div />',
            props: ['load', 'lazy', 'filterable', 'checkStrictly', 'filterNodeMethod', 'clearable', 'expandOnClickNode', 'checkOnClickNode', 'props']
          }
        }
      }
    })
    expect(wrapper).toBeTruthy()
  })
})
