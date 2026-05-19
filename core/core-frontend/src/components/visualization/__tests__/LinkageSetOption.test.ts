import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: () => ({})
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/utils/propTypes', () => ({
  propTypes: { string: { type: String } }
}))

vi.mock('@/config/axios', () => ({}))

import LinkageSetOption from '../LinkageSetOption.vue'

const stubs = {
  ElPopover: {
    template: '<div class="popover"><slot /><slot name="reference" /></div>',
    props: ['placement', 'width', 'trigger']
  },
  ElRow: { template: '<div><slot /></div>' },
  ElRadioGroup: {
    template: '<div><slot /></div>',
    props: ['modelValue'],
    emits: ['update:modelValue', 'change']
  },
  ElRadio: { template: '<label><slot /></label>', props: ['value'] },
  ElIcon: { template: '<i><slot /></i>' },
  Setting: { template: '<svg />' }
}

describe('LinkageSetOption', () => {
  it('renders successfully with actionSelection prop', () => {
    const wrapper = shallowMount(LinkageSetOption, {
      props: {
        actionSelection: { linkageActive: 'custom' }
      },
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders the linkage setting label text', () => {
    const wrapper = shallowMount(LinkageSetOption, {
      props: {
        actionSelection: { linkageActive: 'custom' }
      },
      global: { stubs }
    })
    expect(wrapper.text()).toContain('visualization.linkage_setting')
  })

  it('renders radio group for linkage options', () => {
    const wrapper = shallowMount(LinkageSetOption, {
      props: {
        actionSelection: { linkageActive: 'auto' }
      },
      global: { stubs }
    })
    expect(wrapper.find('div').exists()).toBe(true)
  })
})
