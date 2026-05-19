import { defineComponent } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('element-plus-secondary', () => ({
  ElMessage: { success: vi.fn(), error: vi.fn() },
  ElLoading: { service: () => ({ close: vi.fn() }) }
}))

vi.mock('@/api/datasource', () => ({
  getDeEngine: vi.fn()
}))

vi.mock('@/api/login', () => ({
  querySymmetricKey: vi.fn()
}))

vi.mock('@/views/visualized/data/datasource/form/option', () => ({
  dsTypes: [{ name: 'MySQL', type: 'mysql' }],
  Node: class Node {}
}))

vi.mock('@/components/custom-password', () => ({
  CustomPassword: { template: '<input type="password" />' }
}))

vi.mock('@/utils/encryption', () => ({
  symmetricDecrypt: () => '{}'
}))

vi.mock('@/components/plugin', () => ({
  XpackComponent: { template: '<div class="xpack-stub" />' }
}))

import EngineEdit from '../EngineEdit.vue'

const globalStubs = {
  ElDrawer: defineComponent({
    name: 'ElDrawer',
    props: ['modelValue'],
    template: '<div v-if="modelValue"><slot /><slot name="footer" /></div>'
  }),
  ElForm: { template: '<form><slot /></form>' },
  ElFormItem: { template: '<div><slot /></div>' },
  ElInput: { template: '<input />', props: ['modelValue'] },
  ElInputNumber: { template: '<input type="number" />' },
  ElSelect: { template: '<select><slot /></select>' },
  ElOption: { template: '<option><slot /></option>' },
  ElButton: { template: '<button><slot /></button>' },
  ElRow: { template: '<div><slot /></div>' },
  ElCol: { template: '<div><slot /></div>' },
  ElIcon: { template: '<i><slot /></i>' },
  Icon: { template: '<span><slot /></span>' },
  CustomPassword: { template: '<input type="password" />' },
  XpackComponent: { template: '<div class="xpack-stub" />' }
}

describe('EngineEdit', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(EngineEdit, { global: { stubs: globalStubs } })
    expect(wrapper.exists()).toBe(true)
  })

  it('exposes edit method', () => {
    const wrapper = shallowMount(EngineEdit, { global: { stubs: globalStubs } })
    expect(typeof (wrapper.vm as any).edit).toBe('function')
  })

  it('drawer is hidden by default', () => {
    const wrapper = shallowMount(EngineEdit, { global: { stubs: globalStubs } })
    expect(wrapper.find('.el-drawer-stub').exists()).toBe(false)
  })
})
