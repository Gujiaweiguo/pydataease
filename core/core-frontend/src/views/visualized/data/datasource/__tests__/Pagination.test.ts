import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

import Pagination from '../form/Pagination.vue'

const globalStubs = {
  ElSelect: { template: '<select><slot /></select>' },
  ElOption: { template: '<option><slot /></option>' },
  ElTable: { template: '<table><slot /></table>' },
  ElTableColumn: { template: '<col />' },
  ElInput: { template: '<input />', props: ['modelValue'] }
}

describe('Pagination', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(Pagination, {
      props: {
        page: { pageType: '', requestData: [], responseData: [] }
      },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('displays pagination method label', () => {
    const wrapper = shallowMount(Pagination, {
      props: {
        page: { pageType: 'empty', requestData: [], responseData: [] }
      },
      global: { stubs: globalStubs }
    })
    expect(wrapper.text()).toContain('api_pagination.pagination_method')
  })

  it('shows request table when pageType is not empty', () => {
    const wrapper = shallowMount(Pagination, {
      props: {
        page: {
          pageType: 'pageNumber',
          requestData: [
            { parameterName: 'Page', builtInParameterName: '${pageNumber}', requestParameterName: '', parameterDefaultValue: '' }
          ],
          responseData: [
            { parameterName: 'Total', resolutionPath: '', resolutionPathType: 'totalNumber' }
          ]
        }
      },
      global: { stubs: globalStubs }
    })
    expect(wrapper.text()).toContain('api_pagination.pagination_method')
  })
})
