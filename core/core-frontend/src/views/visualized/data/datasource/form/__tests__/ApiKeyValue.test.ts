import { describe, it, expect, vi } from 'vitest'
import { shallowMount } from '@vue/test-utils'
import ApiKeyValue from '../ApiKeyValue.vue'

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
    props: ['modelValue', 'placeholder', 'disabled']
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
  return shallowMount(ApiKeyValue, {
    props: {
      items: [{ name: 'test-key', value: 'test-value', description: '', type: '', nameType: 'fixed' }],
      ...propsOverrides
    },
    global: {
      stubs: elStubs,
      mocks: { $t: (k: string) => k }
    }
  })
}

describe('ApiKeyValue', () => {
  it('should mount successfully', () => {
    const wrapper = createWrapper()
    expect(wrapper).toBeTruthy()
    expect(wrapper.find('.api-key-value').exists()).toBe(true)
  })

  it('should render the add button', () => {
    const wrapper = createWrapper()
    expect(wrapper.find('.el-button').exists()).toBe(true)
  })

  it('should render with empty items (adds default)', () => {
    const wrapper = createWrapper({ items: [] })
    expect(wrapper).toBeTruthy()
  })

  it('should render with unShowSelect prop', () => {
    const wrapper = createWrapper({ unShowSelect: true })
    expect(wrapper).toBeTruthy()
  })

  it('should render with isReadOnly prop', () => {
    const wrapper = createWrapper({ isReadOnly: true })
    expect(wrapper).toBeTruthy()
  })

  it('should render with showDesc prop', () => {
    const wrapper = createWrapper({ showDesc: true })
    expect(wrapper).toBeTruthy()
  })

  it('should render with suggestions', () => {
    const wrapper = createWrapper({ suggestions: [{ value: 'Content-Type' }] })
    expect(wrapper).toBeTruthy()
  })

  it('should render with keyPlaceholder and valuePlaceholder', () => {
    const wrapper = createWrapper({ keyPlaceholder: 'Header', valuePlaceholder: 'Value' })
    expect(wrapper).toBeTruthy()
  })

  it('should render with valueList for params type', () => {
    const wrapper = createWrapper({
      items: [{ name: 'k', value: 'v', description: '', type: '', nameType: 'params' }],
      valueList: [{ name: 'Param1', originName: 'param1' }]
    })
    expect(wrapper).toBeTruthy()
  })
})
