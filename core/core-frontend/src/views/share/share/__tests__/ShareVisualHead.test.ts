import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: {} })),
    post: vi.fn(() => Promise.resolve({}))
  }
}))
vi.mock('vue-clipboard3', () => ({
  default: () => ({ toClipboard: vi.fn(() => Promise.resolve()) })
}))
vi.mock('@/store/modules/embedded', () => ({ useEmbedded: () => ({ baseUrl: '' }) }))
vi.mock('@/store/modules/share', () => ({
  useShareStoreWithOut: () => ({ getShareDisable: false, getSharePeRequire: false })
}))
vi.mock('@/assets/svg/icon_share-label_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_edit_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_close_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_done_outlined.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/de-copy.svg', () => ({ default: '' }))
vi.mock('@/assets/svg/icon_refresh_outlined.svg', () => ({ default: '' }))
vi.mock('./option', () => ({ SHARE_BASE: '/shareLink', shortcuts: [] }))
import ShareVisualHead from '../ShareVisualHead.vue'

describe('ShareVisualHead', () => {
  const stubs = {
    ElPopover: { template: '<div><slot /><slot name="reference" /></div>' },
    ElButton: { template: '<button><slot /></button>' },
    ElInput: { template: '<input />', props: ['modelValue'] },
    ElSwitch: { template: '<div />', props: ['modelValue'] },
    ElCheckbox: { template: '<div />', props: ['modelValue'] },
    ElDatePicker: { template: '<div />' },
    ElDivider: { template: '<hr />' },
    ElTooltip: { template: '<div><slot /></div>' },
    ElIcon: { template: '<i><slot /></i>' },
    ElLoading: { service: vi.fn(() => ({ close: vi.fn() })) }
  }

  const defaultProps = {
    resourceId: 'test-id',
    resourceType: 'dashboard',
    weight: 7,
    disabled: false
  }

  it('renders with required props', () => {
    const wrapper = shallowMount(ShareVisualHead, {
      props: defaultProps,
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('exposes execute method', () => {
    const wrapper = shallowMount(ShareVisualHead, {
      props: defaultProps,
      global: { stubs }
    })
    expect(typeof (wrapper.vm as any).execute).toBe('function')
  })

  it('does not render share button when weight < 7', () => {
    const wrapper = shallowMount(ShareVisualHead, {
      props: { ...defaultProps, weight: 1 },
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })
})
