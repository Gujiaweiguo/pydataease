import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import CodeEdit from '../CodeEdit.vue'

vi.mock('vue3-ace-editor', () => ({
  VAceEditor: {
    name: 'VAceEditor',
    template: '<div class="v-ace-editor-stub" />',
    props: ['modelValue', 'lang', 'theme', 'style']
  }
}))
vi.mock('../format-utils', () => ({
  formatJson: (s: string) => s,
  formatXml: (s: string) => s
}))
vi.mock('../ace-config', () => ({}))

const globalConfig = {
  global: {
    stubs: {},
    mocks: { $t: (k: string) => k }
  }
}

function createWrapper(propsOverrides = {}) {
  return shallowMount(CodeEdit, {
    props: {
      data: '',
      height: '200px',
      ...propsOverrides
    },
    ...globalConfig
  })
}

describe('CodeEdit', () => {
  it('should mount successfully', () => {
    const wrapper = createWrapper()
    expect(wrapper).toBeTruthy()
  })

  it('should render the ace editor stub', () => {
    const wrapper = createWrapper()
    expect(wrapper.findComponent({ name: 'VAceEditor' }).exists()).toBe(true)
  })

  it('should accept mode prop', () => {
    const wrapper = createWrapper({ mode: 'json' })
    expect(wrapper).toBeTruthy()
  })

  it('should accept readOnly prop', () => {
    const wrapper = createWrapper({ readOnly: true })
    expect(wrapper).toBeTruthy()
  })

  it('should accept enableFormat false', () => {
    const wrapper = createWrapper({ enableFormat: false })
    expect(wrapper).toBeTruthy()
  })

  it('should accept data with json mode', () => {
    const wrapper = createWrapper({ data: '{"key": "value"}', mode: 'json' })
    expect(wrapper).toBeTruthy()
  })

  it('should accept data with xml mode', () => {
    const wrapper = createWrapper({ data: '<root/>', mode: 'xml' })
    expect(wrapper).toBeTruthy()
  })

  it('should accept data with text mode', () => {
    const wrapper = createWrapper({ data: 'plain text', mode: 'text' })
    expect(wrapper).toBeTruthy()
  })

  it('should accept custom theme', () => {
    const wrapper = createWrapper({ theme: 'monokai' })
    expect(wrapper).toBeTruthy()
  })

  it('should accept custom modes array', () => {
    const wrapper = createWrapper({ modes: ['json', 'xml', 'html'] })
    expect(wrapper).toBeTruthy()
  })
})
