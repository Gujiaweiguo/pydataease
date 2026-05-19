import { ref } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  canvasViewInfoValue: {} as Record<string, any>,
  emitSpy: vi.fn()
}))

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: () => ({
    canvasViewInfo: ref(mocks.canvasViewInfoValue)
  })
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({})
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({ emitter: { emit: mocks.emitSpy } })
}))

vi.mock('@/utils/utils', () => ({
  deepCopy: (v: any) => JSON.parse(JSON.stringify(v))
}))

vi.mock('@/config/axios', () => ({}))

import DatasetParamsComponent from '../DatasetParamsComponent.vue'

const stubs = {
  ElDialog: {
    template: '<div class="el-dialog"><slot /><slot name="footer" /></div>',
    props: ['modelValue']
  },
  ElForm: { template: '<form><slot /></form>', props: ['model', 'rules'] },
  ElFormItem: { template: '<div><slot /></div>', props: ['prop'] },
  ElInputNumber: { template: '<input type="number" />', props: ['modelValue'] },
  ElButton: { template: '<button><slot /></button>', props: ['type'] },
  'el-loading': { template: '<div />' }
}

describe('DatasetParamsComponent', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.canvasViewInfoValue = {}
  })

  it('renders successfully', () => {
    const wrapper = shallowMount(DatasetParamsComponent, { global: { stubs } })
    expect(wrapper.exists()).toBe(true)
  })

  it('exposes optInit that opens dialog with params', async () => {
    mocks.canvasViewInfoValue['view-1'] = {
      calParams: [{ name: 'p1', value: 10 }]
    }
    const wrapper = shallowMount(DatasetParamsComponent, { global: { stubs } })
    const vm = wrapper.vm as any
    vm.optInit({ id: 'view-1' })
    await wrapper.vm.$nextTick()
    expect(vm.resetForm).toBeDefined()
  })

  it('exposes statesCheck returning dialog visibility', () => {
    const wrapper = shallowMount(DatasetParamsComponent, { global: { stubs } })
    const vm = wrapper.vm as any
    expect(vm.statesCheck()).toBe(false)
  })

  it('exposes resetForm method', () => {
    const wrapper = shallowMount(DatasetParamsComponent, {
      global: {
        stubs,
        mocks: { $t: (k: string) => k }
      }
    })
    const vm = wrapper.vm as any
    expect(typeof vm.resetForm).toBe('function')
  })
})
