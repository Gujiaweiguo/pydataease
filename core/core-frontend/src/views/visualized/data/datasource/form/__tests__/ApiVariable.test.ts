import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import ApiVariable from '../ApiVariable.vue'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))
vi.mock('@/assets/svg/icon_drag_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_delete-trash_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_add_outlined.svg', () => ({ default: '' }))
vi.mock('vuedraggable', () => ({
  default: {
    name: 'draggable',
    template: '<div class="draggable"><slot name="item" :element="{}" :index="0" /></div>'
  }
}))
vi.mock('@/views/visualized/data/dataset/form/util', () => ({
  guid: () => 'test-uuid-123'
}))

const elStubs = {
  'el-row': { template: '<div class="el-row"><slot /></div>', props: ['gutter'] },
  'el-col': { template: '<div class="el-col"><slot /></div>', props: ['span'] },
  'el-icon': { template: '<i class="el-icon"><slot /></i>' },
  'el-input': {
    template: '<input class="el-input" :value="modelValue" />',
    props: ['modelValue', 'placeholder', 'disabled', 'maxlength']
  },
  'el-autocomplete': {
    template: '<input class="el-autocomplete" />',
    props: ['modelValue', 'placeholder']
  },
  'el-select': {
    template: '<select class="el-select"><slot /></select>',
    props: ['modelValue']
  },
  'el-option': {
    template: '<option :value="value">{{ label }}</option>',
    props: ['label', 'value', 'key']
  },
  'el-button': {
    template: '<button class="el-button"><slot name="icon" /><slot /></button>',
    props: ['text', 'disabled']
  },
  Icon: { template: '<i class="icon-stub"><slot /></i>', props: ['name'] }
}

function createWrapper(propsOverrides = {}) {
  return shallowMount(ApiVariable, {
    props: {
      parameters: [
        {
          name: 'param1',
          value: 'val1',
          description: '',
          type: 'text',
          nameType: 'fixed',
          uuid: '1',
          contentType: 'text/plain',
          enable: true
        }
      ],
      ...propsOverrides
    },
    global: {
      stubs: elStubs,
      mocks: { $t: (k: string) => k }
    }
  })
}

describe('ApiVariable', () => {
  it('should mount successfully', () => {
    const wrapper = createWrapper()
    expect(wrapper).toBeTruthy()
    expect(wrapper.find('.api-variable').exists()).toBe(true)
  })

  it('should render the add button', () => {
    const wrapper = createWrapper()
    expect(wrapper.find('.el-button').exists()).toBe(true)
  })

  it('should render with empty parameters (adds default)', () => {
    const wrapper = createWrapper({ parameters: [] })
    expect(wrapper).toBeTruthy()
  })

  it('should render with description prop', () => {
    const wrapper = createWrapper({ description: 'Test description' })
    expect(wrapper).toBeTruthy()
  })

  it('should render with isReadOnly prop', () => {
    const wrapper = createWrapper({ isReadOnly: true })
    expect(wrapper).toBeTruthy()
  })

  it('should render with type prop as body', () => {
    const wrapper = createWrapper({ type: 'body' })
    expect(wrapper).toBeTruthy()
  })

  it('should render with suggestions', () => {
    const wrapper = createWrapper({ suggestions: [{ value: 'test' }] })
    expect(wrapper).toBeTruthy()
  })

  it('should render with valueList', () => {
    const wrapper = createWrapper({
      parameters: [
        {
          name: 'p',
          value: '',
          description: '',
          type: 'text',
          nameType: 'params',
          uuid: '2',
          contentType: 'text/plain',
          enable: true
        }
      ],
      valueList: [{ name: 'V1', originName: 'v1' }]
    })
    expect(wrapper).toBeTruthy()
  })

  it('should render with keyPlaceholder and valuePlaceholder', () => {
    const wrapper = createWrapper({ keyPlaceholder: 'Key', valuePlaceholder: 'Val' })
    expect(wrapper).toBeTruthy()
  })
})
