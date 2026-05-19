import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: 10 })),
    post: vi.fn(() => Promise.resolve({ data: { records: [], total: 0 } }))
  }
}))

vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => ({ baseUrl: '' })
}))

vi.mock('vue-clipboard3', () => ({
  default: () => ({ toClipboard: vi.fn() })
}))

vi.mock('element-plus-secondary', () => ({
  ElMessage: { success: vi.fn(), warning: vi.fn() },
  ElMessageBox: { confirm: vi.fn() }
}))

import ShareTicket from '../ShareTicket.vue'

const globalStubs = {
  ElButton: { template: '<button><slot /><slot name="icon" /></button>', props: ['text'] },
  ElTooltip: { template: '<div><slot /></div>' },
  ElIcon: { template: '<i><slot /></i>' },
  ElCheckbox: { template: '<input type="checkbox" />', props: ['modelValue', 'label'] },
  ElTableColumn: { template: '<div />', props: ['prop', 'label', 'width'] },
  GridTable: {
    template: '<div><slot /></div>',
    props: ['showEmptyImg', 'tableData', 'pagination', 'showPagination']
  },
  TicketEdit: { template: '<div />', props: ['uuid'] },
  Icon: { template: '<i><slot /></i>' }
}

const globalMocks = {
  $t: (k: string) => k
}

describe('ShareTicket', () => {
  const defaultProps = {
    uuid: 'test-uuid-123',
    resourceId: 'resource-123',
    ticketRequire: false
  }

  it('renders without errors', () => {
    const wrapper = shallowMount(ShareTicket, {
      props: defaultProps,
      global: { stubs: globalStubs, mocks: globalMocks }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders ticket title section', () => {
    const wrapper = shallowMount(ShareTicket, {
      props: defaultProps,
      global: { stubs: globalStubs, mocks: globalMocks }
    })
    expect(wrapper.find('.ticket').exists()).toBe(true)
  })

  it('displays the add button for tickets', () => {
    const wrapper = shallowMount(ShareTicket, {
      props: defaultProps,
      global: { stubs: globalStubs, mocks: globalMocks }
    })
    expect(wrapper.find('.ticket-add').exists()).toBe(true)
  })

  it('emits close event when finish is called', async () => {
    const wrapper = shallowMount(ShareTicket, {
      props: defaultProps,
      global: { stubs: globalStubs, mocks: globalMocks }
    })
    const vm = wrapper.vm as any
    vm.close()
    expect(wrapper.emitted('close')).toBeTruthy()
  })
})
