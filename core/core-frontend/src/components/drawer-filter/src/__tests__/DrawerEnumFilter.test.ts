import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import DrawerEnumFilter from '../DrawerEnumFilter.vue'

const mountComponent = () =>
  mount(DrawerEnumFilter, {
    props: {
      optionList: [
        { id: 'opt1', name: 'Option 1' },
        { id: 'opt2', name: 'Option 2' },
        { id: 'opt3', name: 'Option 3' }
      ],
      title: 'Enum Filter'
    }
  })

describe('DrawerEnumFilter', () => {
  it('renders the title and all option names', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('Enum Filter')
    expect(wrapper.text()).toContain('Option 1')
    expect(wrapper.text()).toContain('Option 2')
    expect(wrapper.text()).toContain('Option 3')
  })

  it('toggles active class on item click', async () => {
    const wrapper = mountComponent()

    const items = wrapper.findAll('.item')
    expect(items).toHaveLength(3)
    expect(items[0].classes()).not.toContain('active')

    await items[0].trigger('click')
    expect(items[0].classes()).toContain('active')
  })

  it('emits filter-change with selected ids on click', async () => {
    const wrapper = mountComponent()

    const items = wrapper.findAll('.item')
    await items[0].trigger('click')

    const filterChangeEvents = wrapper.emitted('filter-change')
    expect(filterChangeEvents).toBeTruthy()
    expect(filterChangeEvents?.[0]).toEqual([['opt1']])
  })

  it('toggles selection on repeated click', async () => {
    const wrapper = mountComponent()

    const items = wrapper.findAll('.item')
    await items[0].trigger('click')
    await items[0].trigger('click')

    const filterChangeEvents = wrapper.emitted('filter-change')
    expect(filterChangeEvents?.[1] ?? []).toEqual([[]])
    expect(items[0].classes()).not.toContain('active')
  })

  it('exposes clear method', async () => {
    const wrapper = mountComponent()

    const items = wrapper.findAll('.item')
    await items[0].trigger('click')
    expect(items[0].classes()).toContain('active')
    ;(wrapper.vm as unknown as { clear: () => void }).clear()
    await wrapper.vm.$nextTick()

    expect(items[0].classes()).not.toContain('active')
  })
})
