import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

vi.mock('@/assets/svg/icon-setting.svg', () => ({ default: '' }))
vi.mock('@/components/icon-custom', () => ({
  Icon: { template: '<span><slot /></span>' }
}))
vi.mock('@/utils/propTypes', () => ({
  propTypes: {
    arrayOf: vi.fn(() => ({
      def: vi.fn((v: any) => v)
    })),
    bool: { def: vi.fn((v: any) => v) },
    shape: vi.fn(() => ({})),
    string: { def: vi.fn((v: string) => v) }
  }
}))

import ColumnList from '../ColumnList.vue'

describe('ColumnList', () => {
  const defaultColumns = [
    { label: 'column.name', props: 'name' },
    { label: 'column.status', props: 'status' }
  ]

  it('should render without errors', () => {
    const wrapper = shallowMount(ColumnList, {
      props: { columnNames: defaultColumns },
      global: {
        stubs: {
          'el-dropdown': { template: '<div><slot /><slot name="dropdown" /></div>', props: ['trigger', 'hideOnClick'] },
          'el-dropdown-menu': true,
          'el-main': true,
          'el-button': { template: '<button><slot /><slot name="icon" /></button>', props: ['secondary'] },
          'el-icon': true,
          'el-checkbox': { template: '<label><slot /></label>', props: ['modelValue', 'indeterminate'] },
          'el-checkbox-group': { template: '<div><slot /></div>', props: ['modelValue'] }
        },
        mocks: { $t: (k: string) => k }
      }
    })
    expect(wrapper).toBeTruthy()
  })
})
