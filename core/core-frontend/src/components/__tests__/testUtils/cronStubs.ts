import { defineComponent, h } from 'vue'

export const ElRadioStub = defineComponent({
  name: 'ElRadio',
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    },
    label: {
      type: [String, Number],
      default: ''
    }
  },
  emits: ['update:modelValue'],
  setup(props, { slots, emit }) {
    return () =>
      h(
        'button',
        {
          class: 'el-radio-stub',
          'data-label': String(props.label),
          'data-checked': String(props.modelValue === props.label),
          onClick: () => emit('update:modelValue', props.label)
        },
        slots.default?.()
      )
  }
})

export const ElInputNumberStub = defineComponent({
  name: 'ElInputNumber',
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    },
    min: {
      type: Number,
      default: undefined
    },
    max: {
      type: Number,
      default: undefined
    }
  },
  emits: ['update:modelValue', 'change'],
  setup() {
    return () => h('div', { class: 'el-input-number-stub' })
  }
})

export const ElCheckboxGroupStub = defineComponent({
  name: 'ElCheckboxGroup',
  props: {
    modelValue: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:modelValue'],
  setup(props, { slots }) {
    return () =>
      h(
        'div',
        {
          class: 'el-checkbox-group-stub',
          'data-count': String(props.modelValue.length)
        },
        slots.default?.()
      )
  }
})

export const ElCheckboxStub = defineComponent({
  name: 'ElCheckbox',
  props: {
    label: {
      type: [String, Number],
      default: ''
    }
  },
  emits: ['change'],
  setup(props, { emit }) {
    return () =>
      h(
        'label',
        {
          class: 'el-checkbox-stub',
          'data-label': String(props.label),
          onClick: () => emit('change', props.label)
        },
        String(props.label)
      )
  }
})

export const cronStubs = {
  ElRadio: ElRadioStub,
  ElInputNumber: ElInputNumberStub,
  ElCheckboxGroup: ElCheckboxGroupStub,
  ElCheckbox: ElCheckboxStub
}

export const lastEmission = (wrapper: any, eventName = 'update:modelValue') =>
  wrapper.emitted(eventName)?.at(-1)?.[0]
