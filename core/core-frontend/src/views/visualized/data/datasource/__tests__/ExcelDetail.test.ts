import { defineComponent, nextTick, reactive } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { emitterMock, saveMock, updateMock, uploadFileMock } = vi.hoisted(() => ({
  emitterMock: { emit: vi.fn() },
  saveMock: vi.fn(),
  updateMock: vi.fn(),
  uploadFileMock: vi.fn()
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => `t:${key}` })
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({ emitter: emitterMock })
}))

vi.mock('@/api/datasource', () => ({
  save: saveMock,
  update: updateMock,
  uploadFile: uploadFileMock
}))

vi.mock('element-plus-secondary', () => ({
  ElIcon: defineComponent({
    name: 'ElIcon',
    template: '<i class="icon-stub"><slot /></i>'
  }),
  ElMessage: vi.fn(),
  ElMessageBox: { confirm: vi.fn() }
}))

import ExcelDetail from '../form/ExcelDetail.vue'

const ElFormStub = defineComponent({
  name: 'ElForm',
  template: '<form class="el-form-stub"><slot /></form>'
})

const ElFormItemStub = defineComponent({
  name: 'ElFormItem',
  template: '<div class="el-form-item-stub"><slot /></div>'
})

const ElInputStub = defineComponent({
  name: 'ElInput',
  props: {
    modelValue: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue'],
  template:
    '<input class="el-input-stub" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />'
})

const ElButtonStub = defineComponent({
  name: 'ElButton',
  emits: ['click'],
  template:
    '<button class="el-button-stub" type="button" @click="$emit(\'click\')"><slot /></button>'
})

const ElUploadStub = defineComponent({
  name: 'ElUpload',
  template: '<div class="el-upload-stub"><slot name="trigger" /></div>'
})

const ElTableStub = defineComponent({
  name: 'ElTable',
  template: '<div class="el-table-stub"><slot /></div>'
})

const ElTableColumnStub = defineComponent({
  name: 'ElTableColumn',
  template: '<div class="el-table-column-stub"><slot /></div>'
})

const ElTableV2Stub = defineComponent({
  name: 'ElTableV2',
  template: '<div class="el-table-v2-stub" />'
})

const ElAutoResizerStub = defineComponent({
  name: 'ElAutoResizer',
  template: '<div class="auto-resizer-stub"><slot :height="300" :width="400" /></div>'
})

const ElSelectStub = defineComponent({
  name: 'ElSelect',
  template: '<select class="el-select-stub"><slot /></select>'
})

const ElOptionStub = defineComponent({
  name: 'ElOption',
  template: '<option><slot /></option>'
})

const ElCheckboxStub = defineComponent({
  name: 'ElCheckbox',
  template: '<input class="el-checkbox-stub" type="checkbox" />'
})

const ElInputNumberStub = defineComponent({
  name: 'ElInputNumber',
  template: '<input class="el-input-number-stub" />'
})

const ExcelInfoStub = defineComponent({
  name: 'ExcelInfo',
  props: {
    name: {
      type: String,
      default: ''
    }
  },
  emits: ['del'],
  template:
    '<div class="excel-info-stub">{{ name }}<button class="excel-delete" type="button" @click="$emit(\'del\')" /></div>'
})

const SheetTabsStub = defineComponent({
  name: 'SheetTabs',
  props: {
    tabList: {
      type: Array,
      default: () => []
    }
  },
  emits: ['tab-click'],
  template: `
    <div class="sheet-tabs-stub">
      <button
        v-for="tab in tabList"
        :key="tab.value"
        class="sheet-tab"
        type="button"
        @click="$emit('tab-click', tab)"
      >
        {{ tab.label }}
      </button>
    </div>
  `
})

const IconStub = defineComponent({
  name: 'Icon',
  template: '<span class="custom-icon-stub"><slot /></span>'
})

const mountComponent = (paramOverrides?: Record<string, unknown>) => {
  const param = reactive({
    configuration: [],
    desc: '',
    editType: 0,
    fileName: '',
    id: '0',
    name: '',
    type: 'Excel',
    ...paramOverrides
  })

  const wrapper = shallowMount(ExcelDetail, {
    props: {
      isSupportSetKey: true,
      param
    },
    global: {
      directives: {
        loading: () => undefined
      },
      stubs: {
        ElAutoResizer: ElAutoResizerStub,
        ElButton: ElButtonStub,
        ElCheckbox: ElCheckboxStub,
        ElForm: ElFormStub,
        ElFormItem: ElFormItemStub,
        ElInput: ElInputStub,
        ElInputNumber: ElInputNumberStub,
        ElOption: ElOptionStub,
        ElSelect: ElSelectStub,
        ElTable: ElTableStub,
        ElTableColumn: ElTableColumnStub,
        ElTableV2: ElTableV2Stub,
        ElUpload: ElUploadStub,
        ExcelInfo: ExcelInfoStub,
        Icon: IconStub,
        SheetTabs: SheetTabsStub
      }
    }
  })

  return { param, wrapper }
}

describe('ExcelDetail', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('initializes preview state from an existing configuration', async () => {
    const { wrapper } = mountComponent({
      configuration: [
        {
          fields: [
            {
              checked: true,
              deExtractType: 0,
              fieldType: 'TEXT',
              length: 20,
              name: 'Region',
              originName: 'region',
              primaryKey: false
            }
          ],
          jsonArray: [{ region: 'North' }],
          newSheet: false,
          sheet: true,
          sheetId: 'sheet_1',
          tableName: 'Sheet 1'
        }
      ],
      fileName: 'Workbook.xlsx',
      name: 'Workbook.xlsx'
    })

    ;(wrapper.vm as any).initFromConfiguration()
    await nextTick()

    expect((wrapper.vm as any).sheetFile.name).toBe('Workbook.xlsx')
    expect(wrapper.text()).toContain('Sheet 1')
    expect(wrapper.text()).toContain('Workbook.xlsx')
  })

  it('applies uploaded excel metadata and allows clearing it through the ExcelInfo child', async () => {
    const { wrapper } = mountComponent()

    ;(wrapper.vm as any).appendReplaceExcel({
      code: 0,
      data: {
        excelLabel: 'Uploaded.xlsx',
        sheets: [
          {
            fields: [],
            jsonArray: [],
            newSheet: false,
            sheet: true,
            sheetId: 'sheet_1',
            tableName: 'Sheet 1'
          }
        ]
      }
    })
    await nextTick()

    expect((wrapper.vm as any).sheetFile.name).toBe('Uploaded.xlsx')

    await wrapper.get('.excel-delete').trigger('click')

    expect((wrapper.vm as any).sheetFile.name).toBeUndefined()
  })

  it('shows the upload validation message when uploadStatus is set', async () => {
    const { wrapper } = mountComponent()

    ;(wrapper.vm as any).uploadStatus(true)
    await nextTick()

    expect(wrapper.text()).toContain('t:data_source.please_upload_files')
  })
})
