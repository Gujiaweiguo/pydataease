import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/custom-component/component-list', () => ({
  default: [
    { component: 'text-card', label: 'Text Card' },
    { component: 'image-card', label: 'Image Card' }
  ]
}))

import ComponentList from '../data-visualization/ComponentList.vue'

describe('ComponentList', () => {
  it('renders each configured component label', () => {
    const wrapper = mount(ComponentList)

    const items = wrapper.findAll('.list')
    expect(items).toHaveLength(2)
    expect(items[0].text()).toBe('Text Card')
    expect(items[1].text()).toBe('Image Card')
  })

  it('adds drag metadata to each component item', () => {
    const wrapper = mount(ComponentList)
    const firstItem = wrapper.findAll('.list')[0]

    expect(firstItem.attributes('draggable')).toBe('true')
    expect(firstItem.attributes('data-index')).toBe('0')
    expect(firstItem.attributes('data-id')).toBe('text-card')
  })

  it('writes the dragged index into dataTransfer on dragstart', async () => {
    const wrapper = mount(ComponentList)
    const setData = vi.fn()

    await wrapper.findAll('.list')[1].trigger('dragstart', {
      dataTransfer: { setData }
    })

    expect(setData).toHaveBeenCalledWith('index', '1')
  })
})
