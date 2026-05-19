import { defineComponent, nextTick } from 'vue'
import { flushPromises, shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  codeComInitMock,
  editorState,
  formClearValidateMock,
  formResetFieldsMock,
  getFunctionMock
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
          doc: {
            get length() {
              return doc.length
            }
          },
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
      destroy: vi.fn(),
      setDoc: (value: string) => {
        doc = value
        editor.viewState.state.selection.ranges[0].from = value.length
      }
    }
    return editor
  }

  return {
    codeComInitMock: vi.fn((initial = '') => {
      editorState.current = createEditor(initial)
      return editorState.current
    }),
    editorState,
    formClearValidateMock: vi.fn(),
    formResetFieldsMock: vi.fn(),
    getFunctionMock: vi.fn(async () => [
      { func: 'SUM([Sales])', name: 'Sum', desc: 'sum desc' },
      { func: 'AVG([Profit])', name: 'Avg', desc: 'avg desc' }
    ])
  }
})

vi.mock('@/api/dataset', () => ({
  getFunction: getFunctionMock
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

import CalcFieldEdit from '../form/CalcFieldEdit.vue'

const CodeMirrorStub = defineComponent({
  name: 'CodeMirror',
  methods: {
    codeComInit(initial = '') {
      return codeComInitMock(initial)
    }
  },
  template: '<div class="codemirror-stub" />'
})

const ElButtonStub = defineComponent({
  name: 'ElButton',
  emits: ['click'],
  template: '<button type="button" @click="$emit(\'click\')"><slot /></button>'
})

const ElDialogStub = defineComponent({
  name: 'ElDialog',
  props: { modelValue: { type: Boolean, default: false } },
  template: '<div class="dialog-stub"><slot /><slot name="footer" /></div>'
})

const ElFormStub = defineComponent({
  name: 'ElForm',
  methods: {
    clearValidate() {
      formClearValidateMock()
    },
    resetFields() {
      formResetFieldsMock()
    },
    validate(callback?: (valid: boolean) => void) {
      callback?.(true)
    }
  },
  template: '<form><slot /></form>'
})

const ElIconStub = defineComponent({
  name: 'ElIcon',
  template: '<i><slot /></i>'
})

const ElInputStub = defineComponent({
  name: 'ElInput',
  props: { modelValue: { type: [String, Number], default: '' } },
  emits: ['update:modelValue'],
  methods: {
    onInput(event: Event) {
      this.$emit('update:modelValue', (event.target as HTMLInputElement)?.value)
    }
  },
  template: '<input :value="modelValue" @input="onInput" />'
})

const ElInputNumberStub = defineComponent({
  name: 'ElInputNumber',
  props: { modelValue: { type: [String, Number], default: 0 } },
  emits: ['update:modelValue'],
  methods: {
    onInput(event: Event) {
      this.$emit('update:modelValue', Number((event.target as HTMLInputElement)?.value))
    }
  },
  template: '<input :value="modelValue" @input="onInput" />'
})

const ElOptionStub = defineComponent({
  name: 'ElOption',
  template: '<option><slot /></option>'
})

const ElPopoverStub = defineComponent({
  name: 'ElPopover',
  template: '<div class="popover-stub"><slot name="reference" /><slot /></div>'
})

const ElRowStub = defineComponent({
  name: 'ElRow',
  template: '<div><slot /></div>'
})

const ElScrollbarStub = defineComponent({
  name: 'ElScrollbar',
  template: '<div><slot /></div>'
})

const ElSelectStub = defineComponent({
  name: 'ElSelect',
  props: { modelValue: { type: [String, Number], default: '' } },
  emits: ['update:modelValue'],
  template: '<select><slot /><slot name="prefix" /></select>'
})

const ElTooltipStub = defineComponent({
  name: 'ElTooltip',
  template: '<div><slot /><slot name="content" /></div>'
})

const IconStub = defineComponent({
  name: 'Icon',
  template: '<span><slot /></span>'
})

const mountComponent = () =>
  shallowMount(CalcFieldEdit, {
    global: {
      stubs: {
        CodeMirror: CodeMirrorStub,
        ElButton: ElButtonStub,
        ElDialog: ElDialogStub,
        ElForm: ElFormStub,
        ElFormItem: true,
        ElIcon: ElIconStub,
        ElInput: ElInputStub,
        ElInputNumber: ElInputNumberStub,
        ElOption: ElOptionStub,
        ElPopover: ElPopoverStub,
        ElRow: ElRowStub,
        ElScrollbar: ElScrollbarStub,
        ElSelect: ElSelectStub,
        ElTooltip: ElTooltipStub,
        Icon: IconStub
      }
    }
  })

describe('CalcFieldEdit', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('loads available functions on mount', async () => {
    const wrapper = mountComponent()

    await flushPromises()

    expect(getFunctionMock).toHaveBeenCalledTimes(1)
    expect(wrapper.text()).toContain('SUM([Sales])')
    expect(wrapper.text()).toContain('AVG([Profit])')
  })

  it('initializes the editor with translated field names', async () => {
    const wrapper = mountComponent()
    const dimensionData = [{ id: 'dim_1', name: 'Region', extField: 0, deType: 0 }]
    const quotaData = [{ id: 'quota_1', name: 'Sales', extField: 0, deType: 2, groupType: 'q' }]

    ;(wrapper.vm as any).initEdit(
      { originName: '[dim_1]+[quota_1]', name: 'Calc Sales' },
      dimensionData,
      quotaData
    )
    await nextTick()

    expect((wrapper.vm as any).fieldForm.name).toBe('Calc Sales')
    expect(editorState.current.dispatch).toHaveBeenLastCalledWith(
      expect.objectContaining({
        changes: expect.objectContaining({ insert: '[Region]+[Sales]' })
      })
    )
  })

  it('translates editor content back to field ids', async () => {
    const wrapper = mountComponent()
    const dimensionData = [{ id: 'dim_1', name: 'Region', extField: 0, deType: 0 }]
    const quotaData = [{ id: 'quota_1', name: 'Sales', extField: 0, deType: 2, groupType: 'q' }]

    ;(wrapper.vm as any).initEdit({}, dimensionData, quotaData)
    editorState.current.setDoc('[Region]+[Sales]')
    ;(wrapper.vm as any).setFieldForm()

    expect((wrapper.vm as any).fieldForm.originName).toBe('[dim_1]+[quota_1]')
  })

  it('filters fields and functions from the search inputs', async () => {
    const wrapper = mountComponent()
    const dimensionData = [
      { id: 'dim_1', name: 'Region', extField: 0, deType: 0 },
      { id: 'dim_2', name: 'City', extField: 0, deType: 0 }
    ]
    const quotaData = [{ id: 'quota_1', name: 'Sales', extField: 0, deType: 2, groupType: 'q' }]

    await flushPromises()
    ;(wrapper.vm as any).initEdit({}, dimensionData, quotaData)
    ;(wrapper.vm as any).searchField = 'reg'
    await nextTick()

    expect((wrapper.vm as any).state.dimensionData).toEqual([dimensionData[0]])
    expect((wrapper.vm as any).state.quotaData).toEqual([])
    ;(wrapper.vm as any).searchFunction = 'avg'
    await nextTick()

    expect((wrapper.vm as any).state.functionData).toEqual([
      { func: 'AVG([Profit])', name: 'Avg', desc: 'avg desc' }
    ])
  })
})
