import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/components/visualization/ComponentButton.vue', () => ({
  default: defineComponent({
    name: 'ComponentButton',
    props: ['title', 'iconName', 'showSplitLine'],
    template:
      '<button class="component-button" :data-title="title" :data-split="String(showSplitLine)">{{ title }}</button>'
  })
}))

vi.mock('@/components/visualization/ComponentButtonLabel.vue', () => ({
  default: defineComponent({
    name: 'ComponentButtonLabel',
    props: ['title', 'iconName', 'showSplitLine'],
    template:
      '<button class="component-button-label" :data-title="title" :data-split="String(showSplitLine)">{{ title }}</button>'
  })
}))

import ComponentGroup from '@/components/visualization/ComponentGroup.vue'

const ElPopoverStub = defineComponent({
  name: 'ElPopover',
  props: ['placement', 'width', 'showArrow', 'popperClass'],
  template:
    '<div class="popover-stub" :data-placement="placement" :data-width="String(width)" :data-show-arrow="String(showArrow)" :data-popper-class="popperClass"><div class="reference"><slot name="reference" /></div><div class="content"><slot /></div></div>'
})

const mountComponent = (props: Record<string, unknown> = {}) =>
  mount(ComponentGroup, {
    props: {
      title: 'Charts',
      iconName: { name: 'chart-icon' },
      showSplitLine: true,
      ...props
    },
    global: {
      stubs: {
        ElPopover: ElPopoverStub
      }
    },
    slots: {
      default: '<div class="group-content">Popover Content</div>'
    }
  })

describe('ComponentGroup', () => {
  it('passes placement, width, and theme class to the popover', () => {
    const wrapper = mountComponent({ placement: 'top', baseWidth: 320, themes: 'light' })
    const popover = wrapper.getComponent(ElPopoverStub)

    expect(popover.props('placement')).toBe('top')
    expect(popover.props('width')).toBe(320)
    expect(popover.props('popperClass')).toBe('custom-popover-light')
  })

  it('renders the standard component button by default', () => {
    const wrapper = mountComponent()

    expect(wrapper.find('.component-button').exists()).toBe(true)
    expect(wrapper.find('.component-button-label').exists()).toBe(false)
  })

  it('renders the label variant when isLabel is enabled', () => {
    const wrapper = mountComponent({ isLabel: true })

    expect(wrapper.find('.component-button-label').exists()).toBe(true)
    expect(wrapper.text()).toContain('Popover Content')
  })
})
