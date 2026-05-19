import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import CustomPassword from '../custom-password/src/CustomPassword.vue'

const ElInputStub = defineComponent({
  name: 'ElInput',
  inheritAttrs: false,
  emits: ['update:modelValue'],
  props: {
    iconHideCustom: {
      type: [Object, String],
      default: null
    },
    iconViewCustom: {
      type: [Object, String],
      default: null
    },
    modelValue: {
      type: String,
      default: ''
    }
  },
  template:
    '<input class="password-input-stub" :value="modelValue" :placeholder="$attrs.placeholder" :data-has-view="String(!!iconViewCustom)" :data-has-hide="String(!!iconHideCustom)" @input="$emit(\'update:modelValue\', $event.target.value)" />'
})

describe('CustomPassword', () => {
  const mountComponent = (modelValue = 'secret') =>
    mount(CustomPassword, {
      attrs: {
        placeholder: 'Enter password'
      },
      props: {
        modelValue
      },
      global: {
        stubs: {
          ElInput: ElInputStub
        }
      }
    })

  it('passes the model value, attrs and custom icons to the input', () => {
    const wrapper = mountComponent()
    const input = wrapper.get('.password-input-stub')

    expect((input.element as HTMLInputElement).value).toBe('secret')
    expect(input.attributes('placeholder')).toBe('Enter password')
    expect(input.attributes('data-has-view')).toBe('true')
    expect(input.attributes('data-has-hide')).toBe('true')
  })

  it('emits update:modelValue when the input changes', async () => {
    const wrapper = mountComponent()

    await wrapper.get('.password-input-stub').setValue('new-secret')

    expect(wrapper.emitted('update:modelValue')).toEqual([['new-secret']])
  })

  it('reacts to modelValue prop updates from the parent', async () => {
    const wrapper = mountComponent('initial')

    await wrapper.setProps({ modelValue: 'changed' })

    expect((wrapper.get('.password-input-stub').element as HTMLInputElement).value).toBe('changed')
  })
})
