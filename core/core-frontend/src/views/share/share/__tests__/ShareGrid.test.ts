import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({
  default: {
    get: vi.fn(() => Promise.resolve({ data: {} })),
    post: vi.fn(() => Promise.resolve({ data: [] }))
  }
}))

vi.mock('@/store/modules/interactive', () => ({
  interactiveStoreWithOut: () => ({
    getData: {}
  })
}))

// Mock ShareHandler because it imports vue-clipboard3 which has ESM issues
vi.mock('../ShareHandler.vue', () => ({
  default: { template: '<div />', props: ['inGrid', 'disabled', 'resourceId', 'weight'] }
}))

import ShareGrid from '../ShareGrid.vue'

const globalStubs = {
  ElRow: { template: '<div><slot /></div>' },
  ElCol: { template: '<div><slot /></div>' },
  ElSelect: { template: '<select><slot /></select>', props: ['modelValue'] },
  ElOption: { template: '<option />', props: ['label', 'value'] },
  ElInput: { template: '<input />', props: ['modelValue', 'clearable', 'placeholder'] },
  ElIcon: { template: '<i><slot /></i>' },
  ElTooltip: { template: '<div><slot /></div>' },
  ElTableColumn: {
    template: '<div />',
    props: ['prop', 'label', 'width', 'sortable', 'fixed', 'key', 'showOverflowTooltip']
  },
  GridTable: {
    template: '<div><slot /></div>',
    props: ['showPagination', 'tableData', 'emptyDesc', 'emptyImg']
  },
  ShareHandler: { template: '<div />', props: ['inGrid', 'disabled', 'resourceId', 'weight'] },
  Icon: { template: '<i><slot /></i>' }
}

describe('ShareGrid', () => {
  it('renders without errors', () => {
    const wrapper = shallowMount(ShareGrid, {
      props: { activeName: 'share' },
      global: { stubs: globalStubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('does not render content when activeName is not share', () => {
    const wrapper = shallowMount(ShareGrid, {
      props: { activeName: 'other' },
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.panel-table').exists()).toBe(false)
  })

  it('renders panel-table when activeName is share', () => {
    const wrapper = shallowMount(ShareGrid, {
      props: { activeName: 'share' },
      global: { stubs: globalStubs }
    })
    expect(wrapper.find('.panel-table').exists()).toBe(true)
  })
})
