import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: {} })),
    post: vi.fn(() => Promise.resolve({ data: {} }))
  }
}))

vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => ({ baseUrl: '' })
}))

vi.mock('@/store/modules/share', () => ({
  useShareStoreWithOut: () => ({ getSharePeRequire: false })
}))

vi.mock('vue-clipboard3', () => ({
  default: () => ({ toClipboard: vi.fn() })
}))

vi.mock('element-plus-secondary', () => ({
  ElMessage: { success: vi.fn(), warning: vi.fn() },
  ElLoading: { service: vi.fn(() => ({ close: vi.fn() })) }
}))

import ShareHandler from '../ShareHandler.vue'

const globalStubs = {
  ElButton: { template: '<button><slot /></button>' },
  ElDialog: {
    template: '<div v-if="modelValue"><slot /><slot name="footer" /></div>',
    props: ['modelValue', 'title', 'width', 'closeOnClickModal', 'appendToBody', 'showClose']
  },
  ElInput: { template: '<input />', props: ['modelValue', 'readonly', 'placeholder'] },
  ElForm: { template: '<form><slot /></form>' },
  ElFormItem: { template: '<div><slot /></div>' },
  ElTooltip: { template: '<div><slot /></div>' },
  ElIcon: { template: '<i><slot /></i>' },
  ElSwitch: { template: '<div />', props: ['modelValue', 'size'] },
  ElCheckbox: { template: '<input type="checkbox" />', props: ['modelValue', 'disabled', 'label'] },
  ElDatePicker: {
    template: '<div />',
    props: ['modelValue', 'type', 'placeholder', 'clearable', 'disabledDate', 'valueFormat']
  },
  CustomLinkPwd: { template: '<div />', props: [] },
  TicketDialog: { template: '<div><slot /></div>' },
  ShareTicket: { template: '<div />', props: ['uuid', 'resourceId', 'ticketRequire'] },
  Icon: { template: '<i><slot /></i>' }
}

describe('ShareHandler', () => {
  const defaultProps = {
    resourceId: 'test-resource-123',
    resourceType: 'dashboard',
    weight: 9,
    inGrid: true,
    disabled: false,
    isButton: false
  }

  it('renders without errors', () => {
    const wrapper = shallowMount(ShareHandler, {
      props: defaultProps,
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('does not render grid icon when weight < 7', () => {
    const wrapper = shallowMount(ShareHandler, {
      props: { ...defaultProps, weight: 5, inGrid: true },
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.share-button-icon').exists()).toBe(false)
  })

  it('emits loaded event on mount when not inGrid and weight >= 7', () => {
    const wrapper = shallowMount(ShareHandler, {
      props: { ...defaultProps, inGrid: false, weight: 9 },
      global: { stubs: globalStubs }
    })
    const emitted = wrapper.emitted('loaded')
    expect(emitted).toBeTruthy()
    expect(emitted![0][0]).toHaveProperty('command', 'share')
  })

  it('does not emit loaded event when inGrid is true', () => {
    const wrapper = shallowMount(ShareHandler, {
      props: { ...defaultProps, inGrid: true, weight: 9 },
      global: { stubs: globalStubs }
    })
    expect(wrapper.emitted('loaded')).toBeFalsy()
  })

  it('exposes execute method', () => {
    const wrapper = shallowMount(ShareHandler, {
      props: defaultProps,
      global: { stubs: globalStubs }
    })
    expect(typeof (wrapper.vm as any).execute).toBe('function')
  })
})
