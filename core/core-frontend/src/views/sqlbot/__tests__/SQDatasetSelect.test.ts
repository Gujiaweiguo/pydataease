import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
vi.mock('@/api/aiSqlBot', () => ({ findDvSqlBotDataset: vi.fn(() => Promise.resolve({ data: [] })) }))
vi.mock('@/store/modules/data-visualization/dvMain', () => {
  const dvInfo = { value: { id: null }, __v_isRef: true }
  return { dvMainStoreWithOut: () => ({ dvInfo }) }
})
vi.mock('@element-plus/icons-vue', () => ({ Refresh: { template: '<i />' } }))
import SQDatasetSelect from '../SQDatasetSelect.vue'

describe('SQDatasetSelect', () => {
  const stubs = {
    ElRow: { template: '<div><slot /></div>' },
    ElSelect: { template: '<select><slot /></select>' },
    ElOption: { template: '<option><slot /></option>' },
    ElButton: { template: '<button><slot /></button>' }
  }

  it('renders with default state', () => {
    const wrapper = shallowMount(SQDatasetSelect, {
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('renders assistant container', () => {
    const wrapper = shallowMount(SQDatasetSelect, {
      global: { stubs }
    })
    expect(wrapper.find('.de-sq-assistant').exists()).toBe(true)
  })

  it('accepts assistantId prop', () => {
    const wrapper = shallowMount(SQDatasetSelect, {
      props: { assistantId: 'bot-123' },
      global: { stubs }
    })
    expect(wrapper.props('assistantId')).toBe('bot-123')
  })

  it('renders dataset select component', () => {
    const wrapper = shallowMount(SQDatasetSelect, {
      global: { stubs }
    })
    expect(wrapper.find('.de-sq-select').exists()).toBe(true)
  })

  it('renders refresh button', () => {
    const wrapper = shallowMount(SQDatasetSelect, {
      global: { stubs }
    })
    expect(wrapper.find('.de-sq-button').exists()).toBe(true)
  })
})
