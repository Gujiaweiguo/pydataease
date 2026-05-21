import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

import OrgCell from '../OrgCell.vue'

const globalStubs = {
  ElIcon: { template: '<i><slot /></i>' }
}

const mountCell = (props = {}) =>
  shallowMount(OrgCell, {
    props: { label: 'Org Unit', ...props },
    global: { stubs: globalStubs }
  })

describe('OrgCell', () => {
  it('renders the label text', () => {
    const wrapper = mountCell({ label: 'My Org' })
    expect(wrapper.text()).toContain('My Org')
  })

  it('emits click with "all" when nextlevel is false and left area clicked', async () => {
    const wrapper = mountCell({ nextlevel: false })
    await wrapper.find('.left-area').trigger('click')
    const clickEvents = wrapper.emitted('click')
    expect(clickEvents).toBeTruthy()
    expect(clickEvents?.[0]).toEqual(['all'])
  })

  it('emits click with "left" when nextlevel is true and left area clicked', async () => {
    const wrapper = mountCell({ nextlevel: true })
    await wrapper.find('.left-area').trigger('click')
    expect(wrapper.emitted('click')?.[0]).toEqual(['left'])
  })

  it('emits click with "right" when nextlevel is true and right area clicked', async () => {
    const wrapper = mountCell({ nextlevel: true })
    await wrapper.find('.right-area').trigger('click')
    expect(wrapper.emitted('click')?.[0]).toEqual(['right'])
  })

  it('shows tips text when provided and nextlevel is true', () => {
    const wrapper = mountCell({ tips: '5 members', nextlevel: true })
    expect(wrapper.text()).toContain('5 members')
  })
})
