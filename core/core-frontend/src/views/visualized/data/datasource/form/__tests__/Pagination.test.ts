import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import Pagination from '../Pagination.vue'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))
vi.mock('lodash-es', () => ({
  cloneDeep: (v: any) => JSON.parse(JSON.stringify(v))
}))

const elStubs = {
  'el-select': {
    template: '<select class="el-select"><slot /></select>',
    props: ['modelValue']
  },
  'el-option': {
    template: '<option :value="value">{{ label }}</option>',
    props: ['label', 'value', 'key']
  },
  'el-table': {
    template: '<div class="el-table"><slot /></div>',
    props: ['data']
  },
  'el-table-column': {
    template: '<div class="el-table-column"><slot name="default" :row="{ parameterDefaultValue: \'\', builtInParameterName: \'${pageNumber}\', resolutionPath: \'\', resolutionPathType: \'totalNumber\' }" /></div>',
    props: ['prop', 'label', 'width']
  },
  'el-input': {
    template: '<input class="el-input" :value="modelValue" />',
    props: ['modelValue', 'placeholder']
  }
}

function createWrapper(propsOverrides = {}) {
  return shallowMount(Pagination, {
    props: {
      page: {
        pageType: 'empty',
        requestData: [],
        responseData: []
      },
      ...propsOverrides
    },
    global: {
      stubs: elStubs,
      mocks: { $t: (k: string) => k }
    }
  })
}

describe('Pagination', () => {
  it('should mount successfully', () => {
    const wrapper = createWrapper()
    expect(wrapper).toBeTruthy()
    expect(wrapper.find('.api-pagination').exists()).toBe(true)
  })

  it('should render page type select', () => {
    const wrapper = createWrapper()
    expect(wrapper.find('.el-select').exists()).toBe(true)
  })

  it('should render with pageNumber pageType', () => {
    const wrapper = createWrapper({
      page: {
        pageType: 'pageNumber',
        requestData: [],
        responseData: []
      }
    })
    expect(wrapper).toBeTruthy()
    expect(wrapper.findAll('.el-table').length).toBe(2)
  })

  it('should render with cursor pageType', () => {
    const wrapper = createWrapper({
      page: {
        pageType: 'cursor',
        requestData: [],
        responseData: []
      }
    })
    expect(wrapper).toBeTruthy()
    expect(wrapper.findAll('.el-table').length).toBe(2)
  })

  it('should render with empty pageType (no tables)', () => {
    const wrapper = createWrapper({
      page: {
        pageType: 'empty',
        requestData: [],
        responseData: []
      }
    })
    expect(wrapper).toBeTruthy()
    expect(wrapper.findAll('.el-table').length).toBe(0)
  })

  it('should render with default empty page prop', () => {
    const wrapper = shallowMount(Pagination, {
      props: { page: {} },
      global: { stubs: elStubs, mocks: { $t: (k: string) => k } }
    })
    expect(wrapper).toBeTruthy()
  })
})
