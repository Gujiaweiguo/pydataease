import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import ApiBody from '../ApiBody.vue'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))
vi.mock('@/utils/propTypes', () => ({
  propTypes: {
    bool: { def: () => ({ type: Boolean, default: false }) },
    string: { def: () => ({ type: String, default: '' }) }
  }
}))

const elStubs = {
  'el-radio-group': {
    template: '<div class="el-radio-group"><slot /></div>',
    props: ['modelValue']
  },
  'el-radio': {
    template: '<label class="el-radio"><slot /></label>',
    props: ['label', 'disabled']
  },
  'api-variable': { template: '<div class="api-variable-stub" />' },
  'code-edit': { template: '<div class="code-edit-stub" />' }
}

function createWrapper(propsOverrides = {}) {
  return shallowMount(ApiBody, {
    props: {
      body: {
        raw: '',
        typeChange: '',
        format: '',
        jsonSchema: '',
        type: 'Form_Data',
        kvs: [{ name: 'k1', value: 'v1', type: 'text', description: '' }]
      },
      headers: [],
      ...propsOverrides
    },
    global: {
      stubs: elStubs,
      mocks: { $t: (k: string) => k }
    }
  })
}

describe('ApiBody', () => {
  it('should mount successfully', () => {
    const wrapper = createWrapper()
    expect(wrapper).toBeTruthy()
    expect(wrapper.find('.radio-group_api').exists()).toBe(true)
  })

  it('should render radio group for body type selection', () => {
    const wrapper = createWrapper()
    expect(wrapper.find('.el-radio-group').exists()).toBe(true)
  })

  it('should show api-variable when body type is Form_Data', () => {
    const wrapper = createWrapper({ body: { type: 'Form_Data', kvs: [], raw: '', typeChange: '' } })
    expect(wrapper.find('.api-variable-stub').exists()).toBe(true)
  })

  it('should show api-variable when body type is WWW_FORM', () => {
    const wrapper = createWrapper({ body: { type: 'WWW_FORM', kvs: [], raw: '', typeChange: '' } })
    expect(wrapper.find('.api-variable-stub').exists()).toBe(true)
  })

  it('should show code-edit when body type is JSON', () => {
    const wrapper = createWrapper({ body: { type: 'JSON', kvs: [], raw: '{"test":1}', typeChange: '' } })
    expect(wrapper.find('.code-edit-stub').exists()).toBe(true)
  })

  it('should show code-edit when body type is XML', () => {
    const wrapper = createWrapper({ body: { type: 'XML', kvs: [], raw: '<root/>', typeChange: '' } })
    expect(wrapper.find('.code-edit-stub').exists()).toBe(true)
  })

  it('should show code-edit when body type is Raw', () => {
    const wrapper = createWrapper({ body: { type: 'Raw', kvs: [], raw: 'plain', typeChange: '' } })
    expect(wrapper.find('.code-edit-stub').exists()).toBe(true)
  })

  it('should render with default body prop', () => {
    const wrapper = shallowMount(ApiBody, {
      props: { headers: [] },
      global: { stubs: elStubs, mocks: { $t: (k: string) => k } }
    })
    expect(wrapper).toBeTruthy()
  })

  it('should render with isReadOnly prop', () => {
    const wrapper = createWrapper({ isReadOnly: true })
    expect(wrapper).toBeTruthy()
  })
})
