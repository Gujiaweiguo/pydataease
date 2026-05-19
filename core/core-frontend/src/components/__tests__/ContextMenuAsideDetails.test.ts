import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/components/data-visualization/canvas/ContextMenuDetails.vue', () => ({
  default: defineComponent({
    name: 'ContextMenuDetails',
    props: ['activePosition'],
    emits: ['close'],
    template:
      '<div class="context-menu-details-stub" :data-position="activePosition" @click="$emit(\'close\', { opt: \'copy\' })"></div>'
  })
}))

import ContextMenuAsideDetails from '@/components/data-visualization/canvas/ContextMenuAsideDetails.vue'

describe('ContextMenuAsideDetails', () => {
  it('renders context menu details in aside mode', () => {
    const wrapper = mount(ContextMenuAsideDetails)

    expect(wrapper.get('.context-menu-details-stub').attributes('data-position')).toBe('aside')
  })

  it('forwards close events from the inner context menu', async () => {
    const wrapper = mount(ContextMenuAsideDetails)

    await wrapper.get('.context-menu-details-stub').trigger('click')

    expect(wrapper.emitted('close')).toEqual([[{ opt: 'copy' }]])
  })

  it('accepts element and index props', () => {
    const wrapper = mount(ContextMenuAsideDetails, {
      props: {
        element: { id: 'a' },
        index: 2
      }
    })

    const props = wrapper.props() as { index: number; element: { id: string } }
    expect(props.index).toBe(2)
    expect(props.element).toEqual({ id: 'a' })
  })
})
