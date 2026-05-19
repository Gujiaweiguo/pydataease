import { defineComponent } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('../ContextMenuDetails.vue', () => ({
  default: defineComponent({
    name: 'ContextMenuDetails',
    props: {
      activePosition: {
        type: String,
        default: ''
      }
    },
    emits: ['close'],
    template:
      '<button class="context-menu-details-stub" :data-position="activePosition" @click="$emit(\'close\', { opt: \'copy\' })"></button>'
  })
}))

import ContextMenuAsideDetails from '../ContextMenuAsideDetails.vue'

describe('ContextMenuAsideDetails', () => {
  it('renders the inner context menu in aside mode', () => {
    const wrapper = shallowMount(ContextMenuAsideDetails)
    const child = wrapper.getComponent({ name: 'ContextMenuDetails' })

    expect(child.props('activePosition')).toBe('aside')
  })

  it('forwards close events from the inner context menu', async () => {
    const wrapper = shallowMount(ContextMenuAsideDetails)
    const child = wrapper.getComponent({ name: 'ContextMenuDetails' })

    child.vm.$emit('close', { opt: 'copy' })
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('close')).toEqual([[{ opt: 'copy' }]])
  })

  it('accepts element and index props', () => {
    const wrapper = shallowMount(ContextMenuAsideDetails, {
      props: {
        element: { id: 'component-1' },
        index: 2
      }
    })

    const props = wrapper.props() as { element: { id: string }; index: number }
    expect(props.element).toEqual({ id: 'component-1' })
    expect(props.index).toBe(2)
  })
})
