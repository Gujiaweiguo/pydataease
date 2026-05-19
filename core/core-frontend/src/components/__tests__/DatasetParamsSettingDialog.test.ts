import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mockState = vi.hoisted(() => ({
  curComponent: { hyperlinks: null as any },
  recordSnapshotCache: vi.fn(),
  checkAddHttp: vi.fn((value: string) => (value.startsWith('http') ? value : `http://${value}`))
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => key })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({ curComponent: mockState.curComponent })
}))

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({ recordSnapshotCache: mockState.recordSnapshotCache })
}))

vi.mock('@/utils/utils', () => ({
  checkAddHttp: mockState.checkAddHttp,
  deepCopy: (value: unknown) => JSON.parse(JSON.stringify(value))
}))

import DatasetParamsSettingDialog from '@/components/visualization/DatasetParamsSettingDialog.vue'

const stubs = {
  ElRow: defineComponent({ name: 'ElRow', template: '<div><slot /></div>' }),
  ElForm: defineComponent({ name: 'ElForm', template: '<form><slot /></form>' }),
  ElFormItem: defineComponent({ name: 'ElFormItem', template: '<div class="item"><slot /></div>' }),
  ElSwitch: defineComponent({
    name: 'ElSwitch',
    props: ['modelValue'],
    emits: ['update:modelValue'],
    template:
      '<input class="switch-stub" type="checkbox" :checked="modelValue" @change="$emit(\'update:modelValue\', $event.target.checked)" />'
  }),
  ElRadioGroup: defineComponent({
    name: 'ElRadioGroup',
    props: ['disabled'],
    template: '<div class="radio-group" :data-disabled="String(disabled)"><slot /></div>'
  }),
  ElRadio: defineComponent({
    name: 'ElRadio',
    props: ['value'],
    template: '<label><slot /></label>'
  }),
  ElInput: defineComponent({
    name: 'ElInput',
    props: ['modelValue', 'disabled'],
    emits: ['update:modelValue'],
    template:
      '<input class="input-stub" :disabled="disabled" :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />'
  }),
  ElButton: defineComponent({
    name: 'ElButton',
    emits: ['click'],
    template: '<button class="button-stub" @click="$emit(\'click\')"><slot /></button>'
  })
}

const mountComponent = (linkInfo: Record<string, unknown>) =>
  mount(DatasetParamsSettingDialog, {
    props: { linkInfo },
    global: { stubs }
  })

describe('DatasetParamsSettingDialog', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockState.curComponent.hyperlinks = null
  })

  it('disables open mode and input when link support is disabled', () => {
    const wrapper = mountComponent({ content: 'a.com', enable: false, openMode: '_self' })

    expect(wrapper.get('.radio-group').attributes('data-disabled')).toBe('true')
    expect(wrapper.get('.input-stub').attributes('disabled')).toBeDefined()
  })

  it('writes normalized hyperlinks to the current component on submit', async () => {
    const wrapper = mountComponent({ content: 'a.com', enable: true, openMode: '_blank' })

    await wrapper.get('.input-stub').setValue('docs.dataease.cn')
    await wrapper.findAll('.button-stub')[0].trigger('click')

    expect(mockState.checkAddHttp).toHaveBeenCalledWith('docs.dataease.cn')
    expect(mockState.curComponent.hyperlinks).toEqual({
      content: 'http://docs.dataease.cn',
      enable: true,
      openMode: '_blank'
    })
    expect(mockState.recordSnapshotCache).toHaveBeenCalledWith('ds-onSubmit')
    expect(wrapper.emitted('onClose')).toEqual([[]])
  })

  it('emits close when cancel is clicked', async () => {
    const wrapper = mountComponent({ content: 'a.com', enable: true, openMode: '_blank' })

    await wrapper.findAll('.button-stub')[1].trigger('click')

    expect(wrapper.emitted('onClose')).toEqual([[]])
  })
})
