import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'

vi.mock('@/config/axios/service', () => ({ service: {} as any, PATH_URL: './', cancelMap: new Map() }))
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/store', () => ({ store: {} }))
vi.mock('pinia', () => ({ defineStore: vi.fn(), storeToRefs: vi.fn(() => ({})), createPinia: vi.fn() }))

vi.mock('@/components/empty-background/src/EmptyBackground.vue', () => ({
  default: { template: '<div class="empty-bg-stub" />' }
}))

vi.mock('./TableBody.vue', () => ({
  default: { template: '<div class="table-body-stub"><slot /></div>' }
}))

vi.mock('@/utils/propTypes', () => ({
  propTypes: {
    arrayOf: vi.fn(() => ({ def: vi.fn(() => () => []) })),
    bool: { def: vi.fn(() => () => false) },
    object: { def: vi.fn(() => () => ({})) },
    array: { def: vi.fn(() => () => []) },
    string: { def: vi.fn(() => () => '') }
  }
}))

describe('GridTable', () => {
  it('renders without errors', async () => {
    const GridTable = (await import('../GridTable.vue')).default
    const wrapper = shallowMount(GridTable, {
      props: {
        tableData: [],
        columns: [],
        pagination: { currentPage: 1, pageSize: 10, total: 0 }
      },
      global: {
        stubs: {
          'el-table': { template: '<div class="el-table-stub"><slot /><template v-for="_ in $slots" /><slot name="empty" /></div>' },
          'el-pagination': { template: '<div class="el-pagination-stub" />' },
          'table-body': { template: '<div class="table-body-stub"><slot /></div>' },
          'empty-background': { template: '<div class="empty-bg-stub" />' }
        }
      }
    })
    expect(wrapper.find('.flex-table').exists()).toBe(true)
  })

  it('renders with table data', async () => {
    const GridTable = (await import('../GridTable.vue')).default
    const wrapper = shallowMount(GridTable, {
      props: {
        tableData: [{ id: 1, name: 'test' }],
        columns: [],
        pagination: { currentPage: 1, pageSize: 10, total: 1 },
        showPagination: true
      },
      global: {
        stubs: {
          'el-table': { template: '<div class="el-table-stub"><slot /><slot name="empty" /></div>' },
          'el-pagination': { template: '<div class="el-pagination-stub" />' },
          'table-body': { template: '<div class="table-body-stub"><slot /></div>' },
          'empty-background': { template: '<div class="empty-bg-stub" />' }
        }
      }
    })
    expect(wrapper.find('.el-table-stub').exists()).toBe(true)
  })
})
