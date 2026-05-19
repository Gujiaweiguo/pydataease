import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { checkAddHttpMock, recordSnapshotCacheMock, storeState } = vi.hoisted(() => ({
  checkAddHttpMock: vi.fn((value: string) =>
    value.startsWith('http') ? value : `http://${value}`
  ),
  recordSnapshotCacheMock: vi.fn(),
  storeState: {
    curComponent: {
      hyperlinks: null as any
    }
  }
}))

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

vi.mock('@/utils/utils', () => ({
  checkAddHttp: checkAddHttpMock,
  deepCopy: (value: unknown) => JSON.parse(JSON.stringify(value))
}))

import HyperlinksDialog from '../visualization/HyperlinksDialog.vue'

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

const ElRadioGroupStub = defineComponent({
  name: 'ElRadioGroup',
  props: {
    disabled: {
      type: Boolean,
      default: false
    }
  },
  template: '<div class="radio-group-stub" :data-disabled="String(disabled)"><slot /></div>'
})

const ElRadioStub = defineComponent({
  name: 'ElRadio',
  props: {
    value: {
      type: String,
      default: ''
    }
  },
  template: '<label class="radio-stub" :data-value="value"><slot /></label>'
})

const ElInputStub = defineComponent({
  name: 'ElInput',
  emits: ['update:modelValue'],
  props: {
    disabled: {
      type: Boolean,
      default: false
    },
    modelValue: {
      type: String,
      default: ''
    }
  },
  template:
    '<input class="input-stub" :disabled="disabled" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />'
})

const ElButtonStub = defineComponent({
  name: 'ElButton',
  emits: ['click'],
  template: '<button type="button" class="button-stub" @click="$emit(\'click\')"><slot /></button>'
})

const mountComponent = (linkInfo: Record<string, unknown>) =>
  mount(HyperlinksDialog, {
    props: { linkInfo },
    global: {
      stubs: {
        ElButton: ElButtonStub,
        ElForm: ElFormStub,
        ElFormItem: ElFormItemStub,
        ElInput: ElInputStub,
        ElRadio: ElRadioStub,
        ElRadioGroup: ElRadioGroupStub,
        ElRow: ElRowStub,
        ElSwitch: ElSwitchStub
      }
    }
  })

describe('HyperlinksDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    storeState.curComponent.hyperlinks = null
  })

  it('disables controls when hyperlink jumping is turned off', () => {
    const wrapper = mountComponent({
      content: 'example.com',
      enable: false,
      openMode: '_self'
    })

    expect((wrapper.get('.tips-area').element as HTMLElement).style.display).toBe('none')
    expect(wrapper.get('.radio-group-stub').attributes('data-disabled')).toBe('true')
    expect(wrapper.get('.input-stub').attributes('disabled')).toBeDefined()
  })

  it('submits the normalized hyperlink into the dv store and records a snapshot', async () => {
    const wrapper = mountComponent({
      content: 'example.com',
      enable: true,
      openMode: '_blank'
    })

    await wrapper.get('.input-stub').setValue('docs.dataease.cn')
    await wrapper.findAll('.button-stub')[0].trigger('click')

    expect(checkAddHttpMock).toHaveBeenCalledWith('docs.dataease.cn')
    expect(storeState.curComponent.hyperlinks).toEqual({
      content: 'http://docs.dataease.cn',
      enable: true,
      openMode: '_blank'
    })
    expect(recordSnapshotCacheMock).toHaveBeenCalledWith('hyper-onSubmit')
    expect(wrapper.emitted('onClose')).toEqual([[]])
  })

  it('emits onClose without mutating the store when cancel is clicked', async () => {
    const wrapper = mountComponent({
      content: 'https://dataease.cn',
      enable: true,
      openMode: '_blank'
    })

    await wrapper.findAll('.button-stub')[1].trigger('click')

    expect(storeState.curComponent.hyperlinks).toBeNull()
    expect(recordSnapshotCacheMock).not.toHaveBeenCalled()
    expect(wrapper.emitted('onClose')).toEqual([[]])
  })
})
