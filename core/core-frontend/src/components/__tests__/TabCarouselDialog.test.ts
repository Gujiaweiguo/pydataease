import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { recordSnapshotCacheMock, storeState } = vi.hoisted(() => ({
  recordSnapshotCacheMock: vi.fn(),
  storeState: {
    curComponent: {
      value: {
        style: {
          carouselEnable: false,
          switchTime: 50
        }
      }
    }
  }
}))

vi.mock('pinia', async () => {
  const actual = await vi.importActual<typeof import('pinia')>('pinia')
  return {
    ...actual,
    storeToRefs: (store: any) => store
  }
})

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => key
  })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => storeState
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: recordSnapshotCacheMock
  })
}))

import TabCarouselDialog from '../visualization/TabCarouselDialog.vue'

const ElRowStub = defineComponent({
  name: 'ElRow',
  template: '<div class="el-row-stub"><slot /></div>'
})

const ElFormStub = defineComponent({
  name: 'ElForm',
  template: '<form class="el-form-stub"><slot /></form>'
})

const ElFormItemStub = defineComponent({
  name: 'ElFormItem',
  template: '<div class="form-item-stub"><slot /></div>'
})

const ElSwitchStub = defineComponent({
  name: 'ElSwitch',
  emits: ['update:modelValue'],
  props: {
    modelValue: {
      type: Boolean,
      default: false
    }
  },
  template:
    '<input class="switch-stub" type="checkbox" :checked="modelValue" @change="$emit(\'update:modelValue\', $event.target.checked)" />'
})

const ElInputStub = defineComponent({
  name: 'ElInput',
  emits: ['update:modelValue', 'change'],
  props: {
    disabled: {
      type: Boolean,
      default: false
    },
    max: {
      type: Number,
      default: 0
    },
    min: {
      type: Number,
      default: 0
    },
    modelValue: {
      type: Number,
      default: 0
    }
  },
  template:
    '<input class="input-stub" type="number" :disabled="disabled" :min="String(min)" :max="String(max)" :value="String(modelValue)" @input="$emit(\'update:modelValue\', Number($event.target.value))" @change="$emit(\'change\')" />'
})

const ElButtonStub = defineComponent({
  name: 'ElButton',
  emits: ['click'],
  template: '<button type="button" class="button-stub" @click="$emit(\'click\')"><slot /></button>'
})

const mountComponent = () =>
  mount(TabCarouselDialog, {
    global: {
      stubs: {
        ElButton: ElButtonStub,
        ElForm: ElFormStub,
        ElFormItem: ElFormItemStub,
        ElInput: ElInputStub,
        ElRow: ElRowStub,
        ElSwitch: ElSwitchStub
      }
    }
  })

describe('TabCarouselDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    storeState.curComponent.value = {
      style: {
        carouselEnable: true,
        switchTime: 8
      }
    }
  })

  it('initializes the dialog form from the current component style', () => {
    const wrapper = mountComponent()

    expect((wrapper.get('.switch-stub').element as HTMLInputElement).checked).toBe(true)
    expect((wrapper.get('.input-stub').element as HTMLInputElement).value).toBe('8')
  })

  it('clamps switchTime to the supported range', async () => {
    const wrapper = mountComponent()
    const input = wrapper.get('.input-stub')

    await input.setValue('1')
    expect((input.element as HTMLInputElement).value).toBe('2')

    await input.setValue('7200')
    expect((input.element as HTMLInputElement).value).toBe('3600')
  })

  it('persists carousel settings and emits onClose on submit', async () => {
    const wrapper = mountComponent()

    wrapper.findComponent(ElSwitchStub).vm.$emit('update:modelValue', false)
    wrapper.findComponent(ElInputStub).vm.$emit('update:modelValue', 120)
    await wrapper.vm.$nextTick()
    await wrapper.findAll('.button-stub')[0].trigger('click')

    expect(storeState.curComponent.value.style).toEqual({
      carouselEnable: false,
      switchTime: 120
    })
    expect(recordSnapshotCacheMock).toHaveBeenCalledWith('onSubmit')
    expect(wrapper.emitted('onClose')).toEqual([[]])
  })
})
