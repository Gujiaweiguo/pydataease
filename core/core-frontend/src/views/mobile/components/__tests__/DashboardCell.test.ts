import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

import DashboardCell from '../DashboardCell.vue'

const globalStubs = {
  ElIcon: { template: '<i><slot /></i>' }
}

const mountCell = (props = {}) =>
  shallowMount(DashboardCell, {
    props: { label: 'Test Label', ...props },
    global: { stubs: globalStubs }
  })

describe('DashboardCell', () => {
  it('renders the label text', () => {
    const wrapper = mountCell({ label: 'My Dashboard' })
    expect(wrapper.text()).toContain('My Dashboard')
  })

  it('emits click when clicked', async () => {
    const wrapper = mountCell()
    await wrapper.find('.dashboard-cell').trigger('click')
    expect(wrapper.emitted('click')).toBeTruthy()
    expect(wrapper.emitted('click')).toHaveLength(1)
  })

  it('does not show switch icon when nextlevel is false', () => {
    const wrapper = mountCell({ nextlevel: false })
    expect(wrapper.find('.switch').exists()).toBe(false)
  })

  it('shows switch icon when nextlevel is true', () => {
    const wrapper = mountCell({ nextlevel: true })
    expect(wrapper.find('.switch').exists()).toBe(true)
  })
})
