import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (k: string) => k }) }))
vi.mock('@/config/axios', () => ({}))
import TicketDialog from '../TicketDialog.vue'

describe('TicketDialog', () => {
  const stubs = {
    ElDialog: { template: '<div v-if="modelValue"><slot /></div>', props: ['modelValue'] }
  }

  it('renders with default state', () => {
    const wrapper = shallowMount(TicketDialog, {
      global: { stubs }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('exposes open method', () => {
    const wrapper = shallowMount(TicketDialog, {
      global: { stubs }
    })
    expect(typeof (wrapper.vm as any).open).toBe('function')
  })

  it('exposes close method', () => {
    const wrapper = shallowMount(TicketDialog, {
      global: { stubs }
    })
    expect(typeof (wrapper.vm as any).close).toBe('function')
  })

  it('renders ticket dialog container', () => {
    const wrapper = shallowMount(TicketDialog, {
      global: { stubs }
    })
    expect(wrapper.find('.ticket-dialog-container').exists()).toBe(true)
  })
})
