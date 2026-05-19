import { defineComponent, h, nextTick } from 'vue'
import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const export2AppCheckMock = vi.hoisted(() => vi.fn())
const validateMock = vi.hoisted(() => vi.fn())

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string, args?: Array<string | number>) =>
      args?.length ? `t:${key}:${args.join(',')}` : `t:${key}`
  })
}))

vi.mock('@/api/visualization/dataVisualization', () => ({
  export2AppCheck: export2AppCheckMock
}))

import AppExportForm from '../de-app/AppExportForm.vue'

const ElDrawerStub = defineComponent({
  name: 'ElDrawer',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue'],
  setup(props, { slots }) {
    return () =>
      h('div', { class: 'el-drawer-stub', 'data-open': String(props.modelValue) }, [
        h('div', { class: 'drawer-title' }, props.title),
        slots.default?.(),
        slots.footer?.()
      ])
  }
})

const ElFormStub = defineComponent({
  name: 'ElForm',
  props: {
    model: {
      type: Object,
      default: () => ({})
    },
    rules: {
      type: Object,
      default: () => ({})
    }
  },
  setup(_, { slots, expose }) {
    expose({
      validate: (callback: (valid: boolean) => void) => validateMock(callback)
    })

    return () => h('form', { class: 'el-form-stub' }, slots.default?.())
  }
})

const ElFormItemStub = defineComponent({
  name: 'ElFormItem',
  props: {
    label: {
      type: String,
      default: ''
    }
  },
  setup(props, { slots }) {
    return () =>
      h('div', { class: 'el-form-item-stub', 'data-label': props.label }, slots.default?.())
  }
})

const ElInputStub = defineComponent({
  name: 'ElInput',
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    },
    placeholder: {
      type: String,
      default: ''
    },
    type: {
      type: String,
      default: 'text'
    }
  },
  emits: ['update:modelValue'],
  setup(props) {
    return () =>
      h('div', {
        class: 'el-input-stub',
        'data-model-value': String(props.modelValue ?? ''),
        'data-placeholder': props.placeholder,
        'data-type': props.type
      })
  }
})

const ElButtonStub = defineComponent({
  name: 'ElButton',
  emits: ['click'],
  setup(_, { slots, emit }) {
    return () =>
      h(
        'button',
        {
          class: 'el-button-stub',
          onClick: () => emit('click')
        },
        slots.default?.()
      )
  }
})

const mountComponent = () =>
  mount(AppExportForm, {
    props: {
      componentData: [
        {
          component: 'VQuery',
          propValue: [{ dataset: { id: 100 } }, { dataset: { id: 101 } }]
        },
        { id: 'view-1', component: 'UserView' },
        {
          component: 'Group',
          propValue: [{ id: 'view-2', component: 'UserView' }]
        },
        {
          component: 'DeTabs',
          propValue: [{ componentData: [{ id: 'view-3', component: 'UserView' }] }]
        }
      ],
      canvasViewInfo: {
        'view-1': { id: 11, tableId: 111 },
        'view-2': { id: 12, tableId: 112 },
        'view-3': { id: 13, tableId: 113 }
      },
      dvInfo: {
        id: 99,
        name: 'Sales Screen'
      }
    },
    global: {
      stubs: {
        ElDrawer: ElDrawerStub,
        ElForm: ElFormStub,
        ElFormItem: ElFormItemStub,
        ElInput: ElInputStub,
        ElButton: ElButtonStub
      }
    }
  })

describe('AppExportForm', () => {
  beforeEach(() => {
    validateMock.mockReset()
    export2AppCheckMock.mockReset()
    validateMock.mockImplementation((callback: (valid: boolean) => void) => callback(true))
    export2AppCheckMock.mockResolvedValue({
      data: {
        checkToken: 'secure-token'
      }
    })
  })

  it('opens the drawer and seeds form fields through init', async () => {
    const wrapper = mountComponent()

    ;(wrapper.vm as unknown as { init: (params: Record<string, unknown>) => void }).init({
      appName: 'Demo App',
      version: '1.0.0',
      required: '2.8.0',
      creator: 'Alex',
      description: 'Mobile dashboard'
    })
    await nextTick()

    const inputs = wrapper.findAllComponents(ElInputStub)

    expect(wrapper.get('.el-drawer-stub').attributes('data-open')).toBe('true')
    expect(inputs[0].props('modelValue')).toBe('Demo App')
    expect(inputs[4].props('modelValue')).toBe('Mobile dashboard')
  })

  it('emits closeDraw and hides the drawer when cancelled', async () => {
    const wrapper = mountComponent()
    ;(wrapper.vm as unknown as { init: (params: Record<string, unknown>) => void }).init({
      appName: 'Demo App',
      version: '1.0.0',
      required: '2.8.0',
      creator: 'Alex',
      description: 'Mobile dashboard'
    })
    await nextTick()

    await wrapper.findAll('button')[0].trigger('click')
    await nextTick()

    expect(wrapper.emitted('closeDraw')).toEqual([[]])
    expect(wrapper.get('.el-drawer-stub').attributes('data-open')).toBe('false')
  })

  it('validates, gathers view info, and emits the final download payload', async () => {
    const wrapper = mountComponent()
    ;(wrapper.vm as unknown as { init: (params: Record<string, unknown>) => void }).init({
      appName: 'Demo App',
      version: '1.0.0',
      required: '2.8.0',
      creator: 'Alex',
      description: 'Mobile dashboard'
    })
    await nextTick()

    await wrapper.findAll('button')[1].trigger('click')
    await flushPromises()

    expect(export2AppCheckMock).toHaveBeenCalledWith({
      dvId: 99,
      viewIds: [11, 12, 13],
      dsIds: [100, 101, 111, 112, 113]
    })
    expect(wrapper.emitted('downLoadApp')?.at(-1)).toEqual([
      expect.objectContaining({
        appName: 'Demo App',
        checkToken: 'secure-token',
        visualizationInfo: JSON.stringify({ id: 99, name: 'Sales Screen' })
      })
    ])
    expect(wrapper.get('.el-drawer-stub').attributes('data-open')).toBe('false')
  })
})
