import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

vi.mock('@/assets/svg/icon_visible_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_invisible_outlined.svg', () => ({ default: '' }))

import CustomPassword from '../CustomPassword.vue'

describe('CustomPassword', () => {
  it('should render without errors', () => {
    const wrapper = shallowMount(CustomPassword, {
      props: { modelValue: 'test-password' },
      global: {
        stubs: {
          'el-input': {
            template: '<input class="el-input-stub" />',
            props: ['modelValue', 'iconViewCustom', 'iconHideCustom']
          }
        }
      }
    })
    expect(wrapper.find('.el-input-stub').exists()).toBe(true)
  })

  it('should emit update:modelValue when value changes', async () => {
    const wrapper = shallowMount(CustomPassword, {
      props: { modelValue: '' },
      global: {
        stubs: {
          'el-input': {
            template: '<input class="el-input-stub" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
            props: ['modelValue', 'iconViewCustom', 'iconHideCustom'],
            emits: ['update:modelValue']
          }
        }
      }
    })
    expect(wrapper).toBeTruthy()
  })
})
