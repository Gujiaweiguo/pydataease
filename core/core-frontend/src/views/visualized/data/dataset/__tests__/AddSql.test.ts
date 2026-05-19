import { defineComponent, ref } from 'vue'
import { flushPromises, shallowMount } from '@vue/test-utils'
import { Base64 } from 'js-base64'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  codeComInitMock,
  getDatasourceListMock,
  getPreviewSqlMock,
  getTablesMock,
  messageErrorMock,
  messageSuccessMock,
  messageWarningMock,
  searchVariableApiMock,
  toClipboardMock
} = vi.hoisted(() => {
  const editorState = { current: null as any }
  const createEditor = (initial = '') => {
    let doc = initial
    const editor = {
      state: {
        doc: {
          toString: () => doc
        }
      },
      viewState: {
        state: {
          selection: {
            ranges: [{ from: doc.length }]
          }
        }
      },
      dispatch: vi.fn((payload: any) => {
        const from = payload?.changes?.from ?? 0
        const to = payload?.changes?.to ?? from
        const insert = payload?.changes?.insert ?? ''
        doc = `${doc.slice(0, from)}${insert}${doc.slice(to)}`
        if (payload?.selection?.anchor !== undefined) {
          editor.viewState.state.selection.ranges[0].from = payload.selection.anchor
        }
      }),
      destroy: vi.fn()
    }
    return editor
  }

  return {
    codeComInitMock: vi.fn((initial = '') => {
      editorState.current = createEditor(initial)
      return editorState.current
    }),
    editorState,
    getDatasourceListMock: vi.fn(async () => [{ id: 'ds_1', name: 'Default DS' }]),
    getPreviewSqlMock: vi.fn(async () => ({
      data: {
        data: [{ sales: 100 }],
        fields: [{ originName: 'sales', deType: 2 }]
      }
    })),
    getTablesMock: vi.fn(async () => [{ tableName: 'orders', name: 'Orders', id: 'tb_1' }]),
    messageErrorMock: vi.fn(),
    messageSuccessMock: vi.fn(),
    messageWarningMock: vi.fn(),
    searchVariableApiMock: vi.fn(async () => ({
      data: [{ id: 'var_1', name: 'Region', type: 'text' }]
    })),
    toClipboardMock: vi.fn(async () => undefined)
  }
})

vi.mock('@/api/dataset', () => ({
  getDatasourceList: getDatasourceListMock,
  getPreviewSql: getPreviewSqlMock,
  getTableField: vi.fn(),
  getTables: getTablesMock
}))

vi.mock('@/api/variable', () => ({
  searchVariableApi: searchVariableApiMock
}))

vi.mock('@/components/icon-custom', () => ({
  Icon: {
    name: 'Icon',
    template: '<span><slot /></span>'
  }
}))

vi.mock('@/components/icon-group/field-list', () => ({
  iconFieldMap: {
    text: 'span',
    time: 'span',
    value: 'span',
    float: 'span',
    location: 'span',
    url: 'span'
  }
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => key })
}))

vi.mock('@/utils/attr', () => ({
  fieldType: ['text', 'time', 'value', 'float', 'value', 'location', 'binary', 'url']
}))

vi.mock('@/utils/ModelUtil', () => ({
  isDesktop: () => false
}))

vi.mock('@vueuse/core', () => ({
  useWindowSize: () => ({ height: ref(900) })
}))

vi.mock('element-plus-secondary', () => ({
  ElIcon: {
    name: 'ElIcon',
    template: '<i><slot /></i>'
  },
  ElMessage: {
    error: messageErrorMock,
    success: messageSuccessMock,
    warning: messageWarningMock
  },
  ElMessageBox: {
    confirm: vi.fn(() => Promise.resolve())
  }
}))

vi.mock(
  'element-plus-secondary/es/components/virtual-list/src/components/fixed-size-list.mjs',
  () => ({
    default: {
      name: 'FixedSizeList',
      template: '<div class="fixed-size-list-stub"><slot :index="0" :style="{}" /></div>'
    }
  })
)

vi.mock('lodash-es', async importOriginal => {
  const actual = await importOriginal<typeof import('lodash-es')>()
  return {
    ...actual,
    debounce: (fn: (...args: any[]) => any) => fn
  }
})

vi.mock('vue-clipboard3', () => ({
  default: () => ({ toClipboard: toClipboardMock })
}))

import AddSql from '../form/AddSql.vue'

const CodeMirrorStub = defineComponent({
  name: 'CodeMirror',
  methods: {
    codeComInit(...args: any[]) {
      return codeComInitMock(...args)
    }
  },
  template: '<div class="codemirror-stub" />'
})

const ElAutoResizerStub = defineComponent({
  name: 'ElAutoResizer',
  template: '<div class="auto-resizer-stub"><slot :height="320" :width="640" /></div>'
})

const ElTableV2Stub = defineComponent({
  name: 'ElTableV2',
  template: '<div class="table-v2-stub" />'
})

const ElButtonStub = defineComponent({
  name: 'ElButton',
  props: { disabled: { type: Boolean, default: false } },
  emits: ['click'],
  template:
    '<button :disabled="disabled" type="button" @click="$emit(\'click\')"><slot /><slot name="icon" /></button>'
})

const ElInputStub = defineComponent({
  name: 'ElInput',
  props: { modelValue: { type: [String, Number], default: '' } },
  emits: ['change', 'update:modelValue'],
  methods: {
    onChange(event: Event) {
      this.$emit('change', (event.target as HTMLInputElement)?.value)
    },
    onInput(event: Event) {
      this.$emit('update:modelValue', (event.target as HTMLInputElement)?.value)
    }
  },
  template: '<input :value="modelValue" @change="onChange" @input="onInput" />'
})

const ElPopoverStub = defineComponent({
  name: 'ElPopover',
  template: '<div><slot name="reference" /><slot /></div>'
})

const mountComponent = (sql = 'select * from orders', overrides: Record<string, unknown> = {}) =>
  shallowMount(AddSql, {
    props: {
      sqlNode: {
        datasourceId: 'ds_1',
        id: 'node_1',
        sql: Base64.encode(sql),
        tableName: 'Orders',
        variables: [],
        ...overrides
      }
    },
    global: {
      directives: {
        loading: {}
      },
      provide: {
        isCross: ref(false)
      },
      stubs: {
        CodeMirror: CodeMirrorStub,
        ElAutoResizer: ElAutoResizerStub,
        ElButton: ElButtonStub,
        ElCascader: true,
        ElCheckbox: true,
        ElCheckboxGroup: true,
        ElDatePicker: true,
        ElDialog: true,
        ElDivider: true,
        ElDrawer: true,
        ElForm: true,
        ElFormItem: true,
        ElInput: ElInputStub,
        ElOption: true,
        ElPagination: true,
        ElPopover: ElPopoverStub,
        ElRadioButton: true,
        ElRadioGroup: true,
        ElScrollbar: true,
        ElSelect: true,
        ElSwitch: true,
        ElTable: true,
        ElTableColumn: true,
        ElTableV2: ElTableV2Stub,
        ElTabs: true,
        ElTabPane: true,
        ElTooltip: true,
        ElTreeSelect: true,
        EmptyBackground: true,
        GridTable: true,
        Icon: true
      }
    }
  })

describe('AddSql', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads datasources, tables, variables, and the decoded SQL on mount', async () => {
    mountComponent('select * from orders')

    await flushPromises()

    expect(codeComInitMock).toHaveBeenCalledWith('select * from orders', true)
    expect(getDatasourceListMock).toHaveBeenCalledTimes(1)
    expect(getTablesMock).toHaveBeenCalledWith({ datasourceId: 'ds_1' })
    expect(searchVariableApiMock).toHaveBeenCalledTimes(1)
  })

  it('toggles the left datasource panel width', async () => {
    const wrapper = mountComponent()

    expect((wrapper.vm as any).showLeft).toBe(true)
    expect((wrapper.vm as any).LeftWidth).toBe(240)
    ;(wrapper.vm as any).handleShowLeft()
    await flushPromises()

    expect((wrapper.vm as any).showLeft).toBe(false)
    expect((wrapper.vm as any).LeftWidth).toBe(0)
  })

  it('emits a saved sql payload with parsed variables', async () => {
    const wrapper = mountComponent('select ${name} from orders')

    await flushPromises()
    ;(wrapper.vm as any).save()

    const saved = wrapper.emitted('save')?.[0]?.[0] as any

    expect(saved.tableName).toBe('Orders')
    expect(saved.sql).toBe(Base64.encode('select ${name} from orders'))
    expect(JSON.parse(saved.sqlVariableDetails)).toEqual([
      expect.objectContaining({ defaultValueScope: 'EDIT', variableName: 'name' })
    ])
  })

  it('loads preview rows and generated columns', async () => {
    const wrapper = mountComponent('select * from orders')

    await flushPromises()
    ;(wrapper.vm as any).getSQLPreview()
    await flushPromises()

    expect(getPreviewSqlMock).toHaveBeenCalledWith(
      expect.objectContaining({
        datasourceId: 'ds_1',
        isCross: false,
        sql: Base64.encode('select * from orders')
      })
    )
    expect((wrapper.vm as any).state.plxTableData).toEqual([{ sales: 100 }])
    expect((wrapper.vm as any).state.fields).toHaveLength(1)
  })
})
