import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import Modal from '../data-visualization/Modal.vue'

describe('Modal', () => {
  it('does not render modal markup when hidden', () => {
    const wrapper = mount(Modal, {
      props: {
        show: false
      }
    })

    expect(wrapper.find('.modal-bg').exists()).toBe(false)
  })

  it('renders slot content when visible', () => {
    const wrapper = mount(Modal, {
      props: {
        show: true
      },
      slots: {
        default: '<div class="content">Modal body</div>'
      }
    })

    expect(wrapper.find('.modal-bg').exists()).toBe(true)
    expect(wrapper.text()).toContain('Modal body')
  })

  it('emits change when the overlay is clicked', async () => {
    const wrapper = mount(Modal, {
      props: {
        show: true
      }
    })

    await wrapper.find('.modal-bg').trigger('click')

    expect(wrapper.emitted('change')).toHaveLength(1)
  })

  it('does not emit change when the inner modal is clicked', async () => {
    const wrapper = mount(Modal, {
      props: {
        show: true
      }
    })

    await wrapper.find('.modal').trigger('click')

    expect(wrapper.emitted('change')).toBeUndefined()
  })
})
