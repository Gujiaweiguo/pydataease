import { defineComponent } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { setShowFinishPageMock, wsCacheMock } = vi.hoisted(() => ({
  setShowFinishPageMock: vi.fn(),
  wsCacheMock: {
    get: vi.fn(),
    set: vi.fn()
  }
}))

vi.mock('@/hooks/web/useCache', () => ({
  useCache: () => ({ wsCache: wsCacheMock })
}))

vi.mock('@/api/datasource', () => ({
  setShowFinishPage: setShowFinishPageMock
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => `t:${key}` })
}))

import FinishPage from '../FinishPage.vue'

const ElButtonStub = defineComponent({
  name: 'ElButton',
  props: {
    disabled: {
      type: Boolean,
      default: false
    }
  },
  emits: ['click'],
  template:
    '<button class="button-stub" type="button" :disabled="disabled" @click="$emit(\'click\')"><slot /></button>'
})

const ElCheckboxStub = defineComponent({
  name: 'ElCheckbox',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    }
  },
  emits: ['change', 'update:modelValue'],
  template: `
    <input
      class="checkbox-stub"
      type="checkbox"
      :checked="modelValue"
      @change="$emit('update:modelValue', $event.target.checked); $emit('change', $event.target.checked)"
    />
  `
})

const ElIconStub = defineComponent({
  name: 'ElIcon',
  template: '<i class="icon-stub"><slot /></i>'
})

const IconStub = defineComponent({
  name: 'Icon',
  template: '<span class="custom-icon-stub"><slot /></span>'
})

const mountComponent = (props?: Record<string, unknown>) =>
  shallowMount(FinishPage, {
    props,
    global: {
      directives: {
        permission: () => undefined
      },
      mocks: {
        $t: (key: string) => `t:${key}`
      },
      stubs: {
        ElButton: ElButtonStub,
        ElCheckbox: ElCheckboxStub,
        ElIcon: ElIconStub,
        Icon: IconStub
      }
    }
  })

describe('FinishPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    wsCacheMock.get.mockReturnValue(false)
  })

  it('initializes the checkbox state from cache', () => {
    wsCacheMock.get.mockReturnValue(true)

    const wrapper = mountComponent()

    expect(wsCacheMock.get).toHaveBeenCalledWith('ds-create-success')
    expect((wrapper.get('.checkbox-stub').element as HTMLInputElement).checked).toBe(true)
  })

  it('emits the three primary actions from the buttons', async () => {
    const wrapper = mountComponent({ disabled: false })
    const buttons = wrapper.findAll('.button-stub')

    await buttons[0].trigger('click')
    await buttons[1].trigger('click')
    await buttons[2].trigger('click')

    expect(wrapper.emitted('continueCreating')).toEqual([[]])
    expect(wrapper.emitted('backToDatasourceList')).toEqual([[]])
    expect(wrapper.emitted('createDataset')).toEqual([[]])
  })

  it('persists the hide-finish-page preference and returns to the list', async () => {
    const wrapper = mountComponent()

    await wrapper.get('.checkbox-stub').setValue(true)

    expect(setShowFinishPageMock).toHaveBeenCalledWith({})
    expect(wsCacheMock.set).toHaveBeenCalledWith('ds-create-success', true)
    expect(wrapper.emitted('backToDatasourceList')).toEqual([[]])
  })
})
