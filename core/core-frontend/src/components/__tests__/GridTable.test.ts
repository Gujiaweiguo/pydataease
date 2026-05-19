import { defineComponent, h, nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('../grid-table/src/TableBody.vue', async () => {
  const { defineComponent } = await vi.importActual<typeof import('vue')>('vue')
  return {
    default: defineComponent({
      name: 'TableBody',
      props: {
        columns: {
          type: Array,
          default: () => []
        }
      },
      setup(props, { slots }) {
        return () =>
          slots
            .default?.()
            .filter(
              (node: any) =>
                !props.columns?.length ||
                props.columns.includes(node.props?.prop) ||
                node.props?.type === 'selection' ||
                node.props?.key === '_operation'
            )
      }
    })
  }
})

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => `translated:${key}`
  })
}))

import GridTable from '../grid-table/src/GridTable.vue'

const tableMethods = vi.hoisted(() => ({
  clearSelection: vi.fn(),
  doLayout: vi.fn(),
  toggleAllSelection: vi.fn(),
  toggleRowSelection: vi.fn()
}))

const ElTableStub = defineComponent({
  name: 'ElTable',
  props: {
    border: {
      type: Boolean,
      default: false
    },
    data: {
      type: Array,
      default: () => []
    }
  },
  setup() {
    return {
      clearSelection: tableMethods.clearSelection,
      doLayout: tableMethods.doLayout,
      toggleAllSelection: tableMethods.toggleAllSelection,
      toggleRowSelection: tableMethods.toggleRowSelection
    }
  },
  template:
    '<div class="el-table-stub" :data-border="String(border)" :data-length="String(data.length)"><slot v-if="data.length" /><div v-else class="empty-slot"><slot name="empty" /></div></div>'
})

const ElPaginationStub = defineComponent({
  name: 'ElPagination',
  props: {
    currentPage: {
      type: Number,
      default: 1
    },
    pageSize: {
      type: Number,
      default: 10
    },
    total: {
      type: Number,
      default: 0
    }
  },
  template:
    '<div class="el-pagination-stub" :data-current-page="String(currentPage)" :data-page-size="String(pageSize)" :data-total="String(total)"></div>'
})

const ColumnStub = defineComponent({
  name: 'ColumnStub',
  props: {
    className: {
      type: String,
      default: ''
    },
    label: {
      type: String,
      default: ''
    },
    prop: {
      type: String,
      default: ''
    },
    type: {
      type: String,
      default: ''
    }
  },
  setup(props) {
    return () => h('div', { class: props.className }, props.label)
  }
})

const mountComponent = (props: Record<string, unknown>) =>
  mount(GridTable, {
    props,
    slots: {
      default: () =>
        h('div', [
          h(ColumnStub, { className: 'column-name', label: 'Name', prop: 'name' }),
          h(ColumnStub, { className: 'column-age', label: 'Age', prop: 'age' }),
          h(ColumnStub, { className: 'column-selection', label: 'Selection', type: 'selection' })
        ])
    },
    global: {
      directives: {
        loading: {}
      },
      stubs: {
        ElTable: ElTableStub,
        ElPagination: ElPaginationStub,
        EmptyBackground: {
          props: ['description', 'imgType'],
          template:
            '<div class="empty-background-stub" :data-description="description" :data-img-type="imgType"></div>'
        }
      }
    }
  })

describe('GridTable', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('passes selected columns into TableBody for filtering', async () => {
    const wrapper = mountComponent({
      columns: ['name'],
      pagination: {},
      tableData: [{ id: 1, name: 'Alice' }]
    })
    await nextTick()

    const tableBody = wrapper.findComponent({ name: 'TableBody' })

    expect(tableBody.exists()).toBe(true)
    expect(tableBody.props('columns')).toEqual(['name'])
  })

  it('shows the translated empty state when there is no data', () => {
    const wrapper = mountComponent({
      isSearch: true,
      pagination: {},
      tableData: []
    })

    expect(wrapper.get('.empty-background-stub').attributes('data-description')).toBe(
      'translated:data_set.no_data'
    )
    expect(wrapper.get('.empty-background-stub').attributes('data-img-type')).toBe('tree')
  })

  it('renders pagination and exposes table selection helpers', async () => {
    const wrapper = mountComponent({
      border: true,
      pagination: { currentPage: 3, pageSize: 20, total: 40 },
      tableData: [{ id: 1, name: 'Alice' }]
    })
    await nextTick()

    expect(wrapper.get('.el-pagination-stub').attributes('data-current-page')).toBe('3')
    expect(wrapper.get('.el-pagination-stub').attributes('data-page-size')).toBe('20')
    expect(wrapper.get('.el-table-stub').attributes('data-border')).toBe('true')

    const exposed = wrapper.vm as unknown as {
      clearSelection: () => void
      toggleAllSelection: () => void
      toggleRowSelection: (row: Record<string, unknown>) => void
    }
    const row = { id: 9 }

    exposed.toggleRowSelection(row)
    exposed.toggleAllSelection()
    exposed.clearSelection()

    expect(tableMethods.toggleRowSelection).toHaveBeenCalledWith(row, true)
    expect(tableMethods.toggleAllSelection).toHaveBeenCalledTimes(1)
    expect(tableMethods.clearSelection).toHaveBeenCalledTimes(1)
  })
})
