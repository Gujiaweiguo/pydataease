import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

import WorkbranchCell from '../Workbranch.vue'

const globalStubs = {
  ElIcon: { template: '<i><slot /></i>' }
}

const mountCell = (props = {}) =>
  shallowMount(WorkbranchCell, {
    props: { label: 'Test Board', time: '2025-01-01', ...props },
    global: { stubs: globalStubs }
  })

describe('WorkbranchCell (mobile)', () => {
  it('renders the label text', () => {
    const wrapper = mountCell({ label: 'Sales Dashboard' })
    expect(wrapper.text()).toContain('Sales Dashboard')
  })

  it('renders the time text', () => {
    const wrapper = mountCell({ time: '2025-06-15 10:30' })
    expect(wrapper.text()).toContain('2025-06-15 10:30')
  })

  it('emits click when the cell is clicked', async () => {
    const wrapper = mountCell()
    await wrapper.find('.workbranch-cell').trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
    expect(wrapper.emitted('click')).toHaveLength(1)
  })

  it('applies the workbranch-cell class', () => {
    const wrapper = mountCell()
    expect(wrapper.find('.workbranch-cell').exists()).toBe(true)
  })
})
