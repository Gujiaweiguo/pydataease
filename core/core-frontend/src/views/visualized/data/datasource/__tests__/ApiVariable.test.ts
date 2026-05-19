import { defineComponent } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => `t:${key}` })
}))

vi.mock('@/views/visualized/data/dataset/form/util', () => ({
  guid: vi.fn(() => 'guid-1')
}))

vi.mock('vuedraggable', () => ({
  default: {
    name: 'draggable',
    props: {
      list: {
        type: Array,
        default: () => []
      }
    },
    template: `
      <div class="draggable-stub">
        <slot name="item" v-for="(element, index) in list" :element="element" :index="index" :key="index" />
      </div>
    `
  }
}))

import ApiVariable from '../form/ApiVariable.vue'

const DraggableStub = defineComponent({
  name: 'draggable',
  props: {
    list: {
      type: Array,
      default: () => []
    }
  },
  template: `
    <div class="draggable-stub">
      <slot name="item" v-for="(element, index) in list" :element="element" :index="index" :key="index" />
    </div>
  `
})

const ElRowStub = defineComponent({
  name: 'ElRow',
  template: '<div class="el-row-stub"><slot /></div>'
})

const ElColStub = defineComponent({
  name: 'ElCol',
  template: '<div class="el-col-stub"><slot /></div>'
})

const ElInputStub = defineComponent({
  name: 'ElInput',
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    }
  },
  emits: ['update:modelValue'],
  template:
    '<input class="el-input-stub" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />'
})

const ElAutocompleteStub = defineComponent({
  name: 'ElAutocomplete',
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    }
  },
  emits: ['update:modelValue'],
  template:
    '<input class="el-autocomplete-stub" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />'
})

const ElSelectStub = defineComponent({
  name: 'ElSelect',
  template: '<select class="el-select-stub"><slot /></select>'
})

const ElOptionStub = defineComponent({
  name: 'ElOption',
  template: '<option><slot /></option>'
})

const ElButtonStub = defineComponent({
  name: 'ElButton',
  emits: ['click'],
  template:
    '<button class="el-button-stub" type="button" :class="$attrs.class" @click="$emit(\'click\')"><slot /></button>'
})

const IconStub = defineComponent({
  name: 'Icon',
  template: '<span class="custom-icon-stub"><slot /></span>'
})

const ElIconStub = defineComponent({
  name: 'ElIcon',
  template: '<i class="icon-stub"><slot /></i>'
})

const mountComponent = (parameters: any[], extraProps?: Record<string, unknown>) =>
  shallowMount(ApiVariable, {
    props: {
      parameters,
      ...extraProps
    },
    global: {
      mocks: {
        $t: (key: string) => `t:${key}`,
        needMock: false
      },
      provide: {
        'api-active-name': 'params'
      },
      stubs: {
        ElAutocomplete: ElAutocompleteStub,
        ElButton: ElButtonStub,
        ElCol: ElColStub,
        ElIcon: ElIconStub,
        ElInput: ElInputStub,
        ElOption: ElOptionStub,
        ElRow: ElRowStub,
        ElSelect: ElSelectStub,
        Icon: IconStub,
        draggable: DraggableStub
      }
    }
  })

describe('ApiVariable', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('adds a default editable row when there are no parameters', () => {
    const parameters: any[] = []

    mountComponent(parameters)

    expect(parameters).toHaveLength(1)
    expect(parameters[0]).toMatchObject({
      contentType: 'text/plain',
      enable: true,
      nameType: 'fixed',
      required: true,
      type: 'text',
      uuid: 'guid-1'
    })
  })

  it('adds another parameter row when the add button is clicked', async () => {
    const parameters = [{ name: 'page', value: '1', description: '', type: 'text' }]
    const wrapper = mountComponent(parameters)

    const buttons = wrapper.findAll('.el-button-stub')
    await buttons[buttons.length - 1].trigger('click')

    expect(parameters).toHaveLength(3)
    expect(parameters[2]).toMatchObject({
      contentType: 'text/plain',
      enable: true,
      nameType: 'fixed',
      type: 'text'
    })
  })

  it('removes a parameter row when more than one row exists', async () => {
    const parameters = [
      { name: 'page', value: '1', description: '', type: 'text' },
      { name: 'size', value: '20', description: '', type: 'text' }
    ]
    const wrapper = mountComponent(parameters)

    await wrapper.find('.api-variable_del').trigger('click')

    expect(parameters).toHaveLength(2)
    expect(parameters[0]).toEqual({ name: 'size', value: '20', description: '', type: 'text' })
    expect(parameters[1]).toMatchObject({
      contentType: 'text/plain',
      enable: true,
      nameType: 'fixed',
      type: 'text'
    })
  })
})
