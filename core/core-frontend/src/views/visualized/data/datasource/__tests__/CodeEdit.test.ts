import { nextTick } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('vue3-ace-editor', () => ({
  VAceEditor: {
    name: 'VAceEditor',
    props: {
      lang: {
        type: String,
        default: ''
      },
      theme: {
        type: String,
        default: ''
      },
      value: {
        type: String,
        default: ''
      }
    },
    emits: ['init', 'update:value'],
    template: '<div class="ace-editor-stub" />'
  }
}))

vi.mock('ace-builds', () => ({
  default: {
    config: { setModuleUrl: vi.fn() },
    require: vi.fn()
  }
}))

vi.mock('../form/ace-config', () => ({}))

import CodeEdit from '../form/CodeEdit.vue'

describe('CodeEdit', () => {
  it('formats JSON data before passing it to the ace editor', async () => {
    const wrapper = shallowMount(CodeEdit, {
      props: {
        data: '{"name":"DataEase"}',
        mode: 'json',
        height: '200px'
      }
    })

    await nextTick()

    expect(wrapper.findComponent({ name: 'VAceEditor' }).props('value')).toBe(
      `{
    "name": "DataEase"
}`
    )
  })

  it('sets read-only mode and forwards custom init handlers', async () => {
    const initMock = vi.fn()
    const setReadOnlyMock = vi.fn()
    const wrapper = shallowMount(CodeEdit, {
      props: {
        data: 'plain text',
        height: '200px',
        init: initMock,
        readOnly: true
      }
    })

    wrapper.findComponent({ name: 'VAceEditor' }).vm.$emit('init', { setReadOnly: setReadOnlyMock })
    await nextTick()

    expect(setReadOnlyMock).toHaveBeenCalledWith(true)
    expect(initMock).toHaveBeenCalled()
  })

  it('skips formatting when formatting is disabled', async () => {
    const wrapper = shallowMount(CodeEdit, {
      props: {
        data: '{"name":"DataEase"}',
        enableFormat: false,
        mode: 'json',
        height: '200px'
      }
    })

    await nextTick()

    expect(wrapper.findComponent({ name: 'VAceEditor' }).props('value')).toBe('{"name":"DataEase"}')
  })
})
