import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import ApiAuthConfig from '../ApiAuthConfig.vue'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

const elStubs = {
  'el-form': { template: '<div class="el-form"><slot /></div>' },
  'el-form-item': {
    template: '<div class="el-form-item"><slot /></div>',
    props: ['label']
  },
  'el-select': {
    template: '<select class="el-select" :value="modelValue" @change="$emit(\'change\', $event.target.value)"><slot /></select>',
    props: ['modelValue', 'placeholder'],
    emits: ['update:modelValue', 'change']
  },
  'el-option': {
    template: '<option :value="value">{{ label }}</option>',
    props: ['label', 'value', 'key']
  },
  'el-row': { template: '<div class="el-row"><slot /></div>', props: ['gutter'] },
  'el-col': { template: '<div class="el-col"><slot /></div>', props: ['span'] },
  'el-input': {
    template: '<input class="el-input" :value="modelValue" />',
    props: ['modelValue', 'placeholder', 'type']
  }
}

function createWrapper(requestOverrides = {}) {
  return shallowMount(ApiAuthConfig, {
    props: {
      request: {
        authManager: {
          verification: '',
          username: '',
          password: '',
          ...requestOverrides
        }
      }
    },
    global: {
      stubs: elStubs,
      mocks: { $t: (k: string) => k }
    }
  })
}

describe('ApiAuthConfig', () => {
  it('should mount successfully', () => {
    const wrapper = createWrapper()
    expect(wrapper).toBeTruthy()
    expect(wrapper.find('.el-form').exists()).toBe(true)
  })

  it('should render verification method select', () => {
    const wrapper = createWrapper()
    expect(wrapper.find('.el-select').exists()).toBe(true)
  })

  it('should not show username/password when verification is not Basic Auth', () => {
    const wrapper = createWrapper({ verification: 'No Auth' })
    // el-col is stubbed so v-if hides it - check that form-items only has the first one
    const formItems = wrapper.findAll('.el-form-item')
    expect(formItems.length).toBe(1)
  })

  it('should show username/password when verification is Basic Auth', () => {
    const wrapper = createWrapper({ verification: 'Basic Auth' })
    const formItems = wrapper.findAll('.el-form-item')
    expect(formItems.length).toBe(3)
  })

  it('should render with default empty authManager', () => {
    const wrapper = shallowMount(ApiAuthConfig, {
      props: { request: { authManager: { verification: '', username: '', password: '' } } },
      global: { stubs: elStubs, mocks: { $t: (k: string) => k } }
    })
    expect(wrapper).toBeTruthy()
  })
})
