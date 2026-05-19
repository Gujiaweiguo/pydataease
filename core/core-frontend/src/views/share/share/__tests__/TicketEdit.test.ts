import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: '' })),
    post: vi.fn(() => Promise.resolve({}))
  }
}))
vi.mock('vue-clipboard3', () => ({
  default: () => ({ toClipboard: vi.fn(() => Promise.resolve()) })
}))
vi.mock('@/assets/svg/de-copy.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_refresh_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_delete-trash_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_add_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/dv-info.svg', () => ({ default: '' }))
import TicketEdit from '../TicketEdit.vue'

describe('TicketEdit', () => {
  const stubs = {
    ElDrawer: {
      template: '<div class="el-drawer"><slot /><slot name="footer" /></div>',
      props: ['modelValue']
    },
    ElButton: { template: '<button><slot /></button>' },
    ElInput: { template: '<input />', props: ['modelValue'] },
    ElInputNumber: { template: '<input type="number" />', props: ['modelValue'] },
    ElForm: { template: '<form><slot /></form>' },
    ElFormItem: { template: '<div><slot /></div>' },
    ElTooltip: { template: '<div><slot /></div>' },
    ElIcon: { template: '<i><slot /></i>' }
  }

  it('renders with default state', () => {
    const wrapper = shallowMount(TicketEdit, {
      props: { uuid: 'test-uuid' },
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('exposes edit method', () => {
    const wrapper = shallowMount(TicketEdit, {
      props: { uuid: 'test-uuid' },
      global: { stubs }
    })
    expect(typeof (wrapper.vm as any).edit).toBe('function')
  })

  it('accepts uuid prop', () => {
    const wrapper = shallowMount(TicketEdit, {
      props: { uuid: 'my-uuid-123' },
      global: { stubs }
    })
    expect(wrapper.props('uuid')).toBe('my-uuid-123')
  })

  it('renders drawer element', () => {
    const wrapper = shallowMount(TicketEdit, {
      props: { uuid: 'test' },
      global: { stubs }
    })
    expect(wrapper.find('.el-drawer').exists()).toBe(true)
  })
})
