import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

import TableTooltip from '../TableTooltip.vue'

describe('TableTooltip', () => {
  const mockTable = {
    updateSortMethodMap: vi.fn(),
    emit: vi.fn()
  } as any

  const mockMeta = {
    field: 'testField'
  } as any

  it('renders component', () => {
    const wrapper = shallowMount(TableTooltip, {
      props: { table: mockTable, meta: mockMeta },
      global: {
        stubs: {
          'el-col': { template: '<div><slot /></div>' },
          'el-row': { template: '<div><slot /></div>' },
          'el-icon': { template: '<div><slot /></div>' },
          SortUp: true,
          SortDown: true,
          Sort: true
        }
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('contains sort buttons', () => {
    const wrapper = shallowMount(TableTooltip, {
      props: { table: mockTable, meta: mockMeta },
      global: {
        stubs: {
          'el-col': { template: '<div><slot /></div>' },
          'el-row': { template: '<div><slot /></div>' },
          'el-icon': { template: '<div><slot /></div>' },
          SortUp: true,
          SortDown: true,
          Sort: true
        }
      }
    })
    expect(wrapper.findAll('.sort-btn').length).toBe(3)
  })
})
