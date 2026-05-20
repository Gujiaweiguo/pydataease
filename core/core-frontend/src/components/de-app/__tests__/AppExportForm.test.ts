import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (k: string) => k
  })
}))
vi.mock('@/api/visualization/dataVisualization', () => ({
  export2AppCheck: vi.fn(() => Promise.resolve({ data: {} }))
}))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

import AppExportForm from '../AppExportForm.vue'

describe('AppExportForm', () => {
  const defaultProps = {
    componentData: {},
    canvasViewInfo: {},
    dvInfo: { id: 'test-id' }
  }

  it('should render without errors', () => {
    const wrapper = shallowMount(AppExportForm, {
      props: defaultProps,
      global: {
        stubs: {
          'el-drawer': {
            template: '<div class="el-drawer-stub"><slot /><slot name="footer" /></div>',
            props: ['title', 'modelValue', 'modalClass', 'size', 'direction']
          },
          'el-form': true,
          'el-form-item': true,
          'el-input': true,
          'el-button': { template: '<button><slot /></button>', props: ['secondary', 'type'] }
        },
        mocks: { $t: (k: string) => k }
      }
    })
    expect(wrapper).toBeTruthy()
  })

  it('should expose init method', () => {
    const wrapper = shallowMount(AppExportForm, {
      props: defaultProps,
      global: {
        stubs: {
          'el-drawer': {
            template: '<div><slot /><slot name="footer" /></div>',
            props: ['title', 'modelValue', 'modalClass', 'size', 'direction']
          },
          'el-form': true,
          'el-form-item': true,
          'el-input': true,
          'el-button': { template: '<button><slot /></button>', props: ['secondary', 'type'] }
        },
        mocks: { $t: (k: string) => k }
      }
    })
    expect(typeof (wrapper.vm as any).init).toBe('function')
  })
})
