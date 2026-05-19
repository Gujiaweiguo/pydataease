import { defineComponent, nextTick, reactive } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { convertFormatMock } = vi.hoisted(() => ({
  convertFormatMock: vi.fn((value: unknown) => ({ schema: value }))
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => `t:${key}` })
}))

vi.mock('../form/convert.js', () => ({
  default: class Convert {
    format(value: unknown) {
      return convertFormatMock(value)
    }
  }
}))

import ApiBody from '../form/ApiBody.vue'

const BODY_TYPE = {
  FORM_DATA: 'Form_Data',
  JSON: 'JSON',
  RAW: 'Raw'
}

const ApiVariableStub = defineComponent({
  name: 'ApiVariable',
  emits: ['change-parameters'],
  template: `
    <div class="api-variable-stub">
      <button class="remove-parameter" type="button" @click="$emit('change-parameters', 0)" />
      <button class="add-parameter" type="button" @click="$emit('change-parameters', { name: 'token', value: 'abc', description: '', type: 'text' })" />
    </div>
  `
})

const CodeEditStub = defineComponent({
  name: 'CodeEdit',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    mode: {
      type: String,
      default: ''
    }
  },
  template: '<div class="code-edit-stub" :data-mode="mode">{{ modelValue }}</div>'
})

const ElRadioGroupStub = defineComponent({
  name: 'ElRadioGroup',
  template: '<div class="radio-group-stub"><slot /></div>'
})

const ElRadioStub = defineComponent({
  name: 'ElRadio',
  props: {
    label: {
      type: String,
      default: ''
    }
  },
  emits: ['change'],
  template:
    '<button class="radio-stub" type="button" :data-label="label" @click="$emit(\'change\', label)"><slot /></button>'
})

const mountComponent = (body: any, headers: any[] = [], valueList: any[] = []) =>
  shallowMount(ApiBody, {
    props: {
      body,
      headers,
      valueList
    },
    global: {
      stubs: {
        ApiVariable: ApiVariableStub,
        CodeEdit: CodeEditStub,
        ElRadio: ElRadioStub,
        ElRadioGroup: ElRadioGroupStub
      }
    }
  })

describe('ApiBody', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('defaults to form data mode and normalizes kv row types on mount', () => {
    const body = {
      raw: '',
      typeChange: '',
      format: '',
      jsonSchema: '',
      type: '',
      kvs: [{ name: 'token', value: 'abc', description: '', type: '' }]
    }

    mountComponent(body)

    expect(body.type).toBe(BODY_TYPE.FORM_DATA)
    expect(body.kvs[0].type).toBe('text')
  })

  it('sets the Content-Type header when switching to JSON mode', async () => {
    const body = {
      raw: '',
      typeChange: '',
      format: '',
      jsonSchema: '',
      type: BODY_TYPE.FORM_DATA,
      kvs: []
    }
    const headers: any[] = []
    const wrapper = mountComponent(body, headers)

    body.type = BODY_TYPE.JSON
    await wrapper.find('[data-label="JSON"]').trigger('click')

    expect(headers[0]).toMatchObject({
      name: 'Content-Type',
      value: 'application/json'
    })
  })

  it('converts valid raw JSON into a schema preview', async () => {
    const body = {
      raw: '',
      typeChange: '',
      format: '',
      jsonSchema: '',
      type: BODY_TYPE.JSON,
      kvs: []
    }

    const reactiveBody = reactive(body)

    mountComponent(reactiveBody)
    reactiveBody.raw = '{"name":"DataEase"}'
    await nextTick()

    expect(convertFormatMock).toHaveBeenCalledWith({ name: 'DataEase' })
    expect(reactiveBody.jsonSchema).toEqual({ schema: { name: 'DataEase' } })
  })

  it('clears the schema preview when raw JSON is invalid', async () => {
    const body = {
      raw: '',
      typeChange: '',
      format: '',
      jsonSchema: 'keep',
      type: BODY_TYPE.JSON,
      kvs: []
    }

    const reactiveBody = reactive(body)

    mountComponent(reactiveBody)
    reactiveBody.raw = '{invalid json}'
    await nextTick()

    expect(reactiveBody.jsonSchema).toBe('')
  })

  it('updates kv rows from the ApiVariable child events', async () => {
    const body = {
      raw: '',
      typeChange: '',
      format: '',
      jsonSchema: '',
      type: BODY_TYPE.FORM_DATA,
      kvs: [{ name: 'old', value: '1', description: '', type: 'text' }]
    }
    const wrapper = mountComponent(body)

    await wrapper.get('.remove-parameter').trigger('click')
    expect(body.kvs).toHaveLength(0)

    await wrapper.get('.add-parameter').trigger('click')
    expect(body.kvs).toEqual([{ name: 'token', value: 'abc', description: '', type: 'text' }])
  })
})
