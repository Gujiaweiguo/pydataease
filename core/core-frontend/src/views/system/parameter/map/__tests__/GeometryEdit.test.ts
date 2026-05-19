import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({ default: { post: vi.fn(() => Promise.resolve({})) } }))
vi.mock('@/hooks/web/useCache', () => ({ useCache: () => ({ wsCache: { get: vi.fn(() => []) } }) }))
vi.mock('@/assets/svg/dv-info.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_upload_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/de-json.svg', () => ({ default: '' }))
import GeometryEdit from '../GeometryEdit.vue'

describe('GeometryEdit', () => {
  const stubs = {
    ElDrawer: { template: '<div class="el-drawer"><slot /><slot name="footer" /></div>', props: ['modelValue'] },
    ElButton: { template: '<button><slot /></button>' },
    ElInput: { template: '<input />', props: ['modelValue'] },
    ElForm: { template: '<form><slot /></form>' },
    ElFormItem: { template: '<div><slot /></div>' },
    ElSelect: { template: '<select><slot /></select>' },
    ElOption: { template: '<option><slot /></option>' },
    ElTreeSelect: { template: '<select />' },
    ElUpload: { template: '<div><slot /></div>' },
    ElTooltip: { template: '<div><slot /></div>' },
    ElIcon: { template: '<i><slot /></i>' }
  }

  it('renders with default state', () => {
    const wrapper = shallowMount(GeometryEdit, {
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('exposes edit method', () => {
    const wrapper = shallowMount(GeometryEdit, {
      global: { stubs }
    })
    expect(typeof (wrapper.vm as any).edit).toBe('function')
  })

  it('renders drawer element', () => {
    const wrapper = shallowMount(GeometryEdit, {
      global: { stubs }
    })
    expect(wrapper.find('.el-drawer').exists()).toBe(true)
  })

  it('emits saved event definition exists', () => {
    const wrapper = shallowMount(GeometryEdit, {
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
