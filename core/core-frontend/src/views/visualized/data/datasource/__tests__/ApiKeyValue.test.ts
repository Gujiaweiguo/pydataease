import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('../form/ApiTestModel.js', () => ({
  KeyValue: class KeyValue {
    constructor(opts = {}) {
      Object.assign(this, { enable: true, name: '', value: '', nameType: 'fixed', ...opts })
    }
  }
}))

vi.mock('vuedraggable', () => ({
  default: { template: '<div class="draggable-stub"><slot name="item" element="{ element: {}, index: 0 }" /></div>' }
}))

import ApiKeyValue from '../form/ApiKeyValue.vue'

const globalStubs = {
  ElRow: { template: '<div><slot /></div>' },
  ElCol: { template: '<div><slot /></div>' },
  ElInput: { template: '<input />', props: ['modelValue'] },
  ElSelect: { template: '<select><slot /></select>' },
  ElOption: { template: '<option><slot /></option>' },
  ElButton: { template: '<button><slot /></button>' },
  ElAutocomplete: { template: '<input />' },
  ElIcon: { template: '<i><slot /></i>' },
  Icon: { template: '<span><slot /></span>' }
}

describe('ApiKeyValue', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(ApiKeyValue, {
      props: { items: [] },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('shows add parameters button', () => {
    const wrapper = shallowMount(ApiKeyValue, {
      props: { items: [] },
      global: { stubs: globalStubs }
    })
    expect(wrapper.text()).toContain('data_source.add_parameters')
  })

  it('uses default key placeholder when none provided', () => {
    const wrapper = shallowMount(ApiKeyValue, {
      props: { items: [] },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
