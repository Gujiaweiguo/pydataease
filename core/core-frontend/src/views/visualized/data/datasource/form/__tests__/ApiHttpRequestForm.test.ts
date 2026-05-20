import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import ApiHttpRequestForm from '../ApiHttpRequestForm.vue'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))
vi.mock('@/store', () => ({ store: {} }))
vi.mock('pinia', () => ({
  defineStore: vi.fn(),
  storeToRefs: vi.fn(() => ({})),
  createPinia: vi.fn()
}))

const elStubs = {
  'el-tabs': {
    template: '<div class="el-tabs"><slot /></div>',
    props: ['modelValue']
  },
  'el-tab-pane': {
    template: '<div class="el-tab-pane"><slot /></div>',
    props: ['label', 'name', 'key']
  },
  'el-tooltip': {
    template: '<div class="el-tooltip"><slot /><slot name="label" /></div>',
    props: ['effect', 'content', 'placement']
  },
  'api-key-value': { template: '<div class="api-key-value-stub" />' },
  'api-variable': { template: '<div class="api-variable-stub" />' },
  'api-body': { template: '<div class="api-body-stub" />' },
  'api-auth-config': { template: '<div class="api-auth-config-stub" />' },
  Pagination: { template: '<div class="pagination-stub" />' }
}

function createWrapper(propsOverrides = {}) {
  return shallowMount(ApiHttpRequestForm, {
    props: {
      request: {
        changeId: '',
        authManager: { verification: '', username: '', password: '' },
        headers: [],
        rest: [],
        arguments: [],
        body: { typeChange: '', kvs: [], type: 'Form_Data' },
        page: { pageType: 'empty', requestData: [], responseData: [] }
      },
      ...propsOverrides
    },
    global: {
      stubs: elStubs,
      mocks: { $t: (k: string) => k }
    }
  })
}

describe('ApiHttpRequestForm', () => {
  it('should mount successfully', () => {
    const wrapper = createWrapper()
    expect(wrapper).toBeTruthy()
    expect(wrapper.find('.request-content').exists()).toBe(true)
  })

  it('should render tabs for different sections', () => {
    const wrapper = createWrapper()
    expect(wrapper.find('.el-tabs').exists()).toBe(true)
  })

  it('should render all tab panes', () => {
    const wrapper = createWrapper()
    const panes = wrapper.findAll('.el-tab-pane')
    expect(panes.length).toBe(5)
  })

  it('should render with default request prop', () => {
    const wrapper = shallowMount(ApiHttpRequestForm, {
      props: {},
      global: { stubs: elStubs, mocks: { $t: (k: string) => k } }
    })
    expect(wrapper).toBeTruthy()
  })

  it('should render with showScript false', () => {
    const wrapper = createWrapper({ showScript: false })
    expect(wrapper).toBeTruthy()
  })

  it('should render with isReadOnly true', () => {
    const wrapper = createWrapper({ isReadOnly: true })
    expect(wrapper).toBeTruthy()
  })

  it('should render with referenced true', () => {
    const wrapper = createWrapper({ referenced: true })
    expect(wrapper).toBeTruthy()
  })

  it('should render with valueList', () => {
    const wrapper = createWrapper({
      valueList: [{ name: 'V1', originName: 'v1' }]
    })
    expect(wrapper).toBeTruthy()
  })
})
