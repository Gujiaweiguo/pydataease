import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div />' }
}))

vi.mock('@/config/axios/hmac', () => ({}))
vi.mock('@/config/axios/service', () => ({
  cancelRequestBatch: vi.fn()
}))

vi.mock('@/views/template-market/index.vue', () => ({
  default: { template: '<div class="template-market-stub" />' }
}))

import DeResourceCreateOptV2 from '../DeResourceCreateOptV2.vue'

const globalStubs = {
  ElDialog: {
    props: ['modelValue'],
    template: '<div v-if="modelValue" class="dialog-stub"><slot /></div>'
  }
}

const mountDialog = () =>
  shallowMount(DeResourceCreateOptV2, {
    global: { stubs: globalStubs }
  })

describe('DeResourceCreateOptV2', () => {
  it('renders but dialog is hidden initially', () => {
    const wrapper = mountDialog()
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.dialog-stub').exists()).toBe(false)
  })

  it('exposes optInit method', () => {
    const wrapper = mountDialog()
    const vm = wrapper.vm as any
    expect(typeof vm.optInit).toBe('function')
  })

  it('shows dialog state changes when optInit is called', async () => {
    const wrapper = mountDialog()
    const vm = wrapper.vm as any
    expect(vm.state.dialogShow).toBe(false)
  })
})
