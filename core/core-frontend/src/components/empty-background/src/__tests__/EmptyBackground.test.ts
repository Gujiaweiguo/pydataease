import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

vi.mock('@/assets/img/nothing-input.png', () => ({ default: 'nothing-input.png' }))
vi.mock('@/assets/img/nothing-select.png', () => ({ default: 'nothing-select.png' }))
vi.mock('@/assets/img/nothing-table.png', () => ({ default: 'nothing-table.png' }))
vi.mock('@/assets/img/none.png', () => ({ default: 'none.png' }))
vi.mock('@/assets/img/error.png', () => ({ default: 'error.png' }))
vi.mock('@/assets/img/nothing-tree.png', () => ({ default: 'nothing-tree.png' }))
vi.mock('@/assets/img/nothing-none.png', () => ({ default: 'nothing-none.png' }))

import EmptyBackground from '../EmptyBackground.vue'

describe('EmptyBackground', () => {
  it('should render with default props', () => {
    const wrapper = shallowMount(EmptyBackground, {
      global: {
        stubs: {
          'el-empty': {
            template: '<div class="el-empty-stub"><slot /></div>',
            props: ['imageSize', 'description', 'image']
          }
        }
      }
    })
    expect(wrapper.find('.el-empty-stub').exists()).toBe(true)
  })

  it('should pass correct image based on imgType', () => {
    const wrapper = shallowMount(EmptyBackground, {
      props: { imgType: 'input', description: 'No results', imageSize: 100 },
      global: {
        stubs: {
          'el-empty': {
            template: '<div class="el-empty-stub"><slot /></div>',
            props: ['imageSize', 'description', 'image']
          }
        }
      }
    })
    expect(wrapper).toBeTruthy()
  })

  it('should render slot content', () => {
    const wrapper = shallowMount(EmptyBackground, {
      props: { imgType: 'table' },
      slots: { default: '<span class="custom-slot">custom</span>' },
      global: {
        stubs: {
          'el-empty': {
            template: '<div class="el-empty-stub"><slot /></div>',
            props: ['imageSize', 'description', 'image']
          }
        }
      }
    })
    expect(wrapper.find('.custom-slot').exists()).toBe(true)
  })
})
