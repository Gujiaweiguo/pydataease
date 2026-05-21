import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

import CanvasCacheDialog from '../CanvasCacheDialog.vue'

const globalStubs = {
  ElDialog: {
    props: ['modelValue'],
    template: '<div v-if="modelValue" class="dialog-stub"><slot /><slot name="footer" /></div>'
  },
  ElButton: {
    template: '<button class="btn-stub" @click="$emit(\'click\')"><slot /></button>',
    emits: ['click']
  },
  ElIcon: { template: '<i><slot /></i>' },
  Icon: { template: '<i><slot /></i>' }
}

const mountDialog = () =>
  shallowMount(CanvasCacheDialog, {
    global: { stubs: globalStubs }
  })

describe('CanvasCacheDialog', () => {
  it('renders but dialog is hidden initially', () => {
    const wrapper = mountDialog()
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.dialog-stub').exists()).toBe(false)
  })

  it('exposes dialogInit method that shows the dialog', async () => {
    const wrapper = mountDialog()
    const vm = wrapper.vm as any
    vm.dialogInit({ resourceId: 'res-1', canvasType: 'dashboard' })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.dialog-stub').exists()).toBe(true)
    expect(wrapper.text()).toContain('visualization.no_save_tips2')
  })

  it('emits doUseCache with true and closes dialog', async () => {
    const wrapper = mountDialog()
    const vm = wrapper.vm as any
    vm.dialogInit({ resourceId: 'res-1', canvasType: 'dataV' })
    await wrapper.vm.$nextTick()

    vm.doUseCache(true)
    await wrapper.vm.$nextTick()

    const doUseCacheEvents = wrapper.emitted('doUseCache')
    expect(doUseCacheEvents).toBeTruthy()
    expect(doUseCacheEvents?.[0]).toEqual([true])
    expect(wrapper.find('.dialog-stub').exists()).toBe(false)
  })

  it('emits doUseCache with false', async () => {
    const wrapper = mountDialog()
    const vm = wrapper.vm as any
    vm.dialogInit({ resourceId: 'res-1', canvasType: 'dashboard' })
    await wrapper.vm.$nextTick()

    vm.doUseCache(false)
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('doUseCache')?.[0]).toEqual([false])
  })
})
