import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import DrawerEnumFilter from '../drawer-filter/src/DrawerEnumFilter.vue'

const mountComponent = () =>
  mount(DrawerEnumFilter, {
    props: {
      optionList: [
        { id: 'a', name: 'Alpha' },
        { id: 'b', name: 'Beta' }
      ],
      title: 'Enum Filter'
    }
  })

describe('DrawerEnumFilter', () => {
  it('renders the title and clickable enum options', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('Enum Filter')
    expect(wrapper.findAll('.item')).toHaveLength(2)
    expect(wrapper.findAll('.item')[0].text()).toBe('Alpha')
  })

  it('toggles option selection and emits the current ids', async () => {
    const wrapper = mountComponent()
    const firstItem = wrapper.findAll('.item')[0]

    await firstItem.trigger('click')
    expect(firstItem.classes()).toContain('active')
    expect(wrapper.emitted('filter-change')).toEqual([[['a']]])

    await firstItem.trigger('click')
    expect(firstItem.classes()).not.toContain('active')
    expect(wrapper.emitted('filter-change')?.[1]).toEqual([[]])
  })

  it('removes all active tags when clear is called', async () => {
    const wrapper = mountComponent()

    await wrapper.findAll('.item')[1].trigger('click')
    expect(wrapper.findAll('.item')[1].classes()).toContain('active')
    ;(wrapper.vm as unknown as { clear: () => void }).clear()
    await wrapper.vm.$nextTick()

    expect(wrapper.findAll('.item')[1].classes()).not.toContain('active')
  })
})
