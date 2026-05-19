import { defineComponent, nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import FilterText from '../filter-text/src/FilterText.vue'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => `translated:${key}` })
}))

const ElButtonStub = defineComponent({
  name: 'ElButton',
  emits: ['click'],
  template:
    '<button class="button-stub" @click="$emit(\'click\')"><slot name="icon" /><slot /></button>'
})

const ElIconStub = defineComponent({
  name: 'ElIcon',
  emits: ['click'],
  template: '<i class="icon-stub" @click="$emit(\'click\')"><slot /></i>'
})

describe('FilterText', () => {
  const mountComponent = (filterTexts: string[] = ['North']) =>
    mount(FilterText, {
      props: {
        filterTexts,
        total: 12
      },
      global: {
        stubs: {
          ElDivider: {
            template: '<span class="divider-stub" />'
          },
          ElButton: ElButtonStub,
          ElIcon: ElIconStub,
          ElTooltip: {
            template: '<span class="tooltip-stub"><slot /></span>'
          },
          Icon: {
            template: '<span class="custom-icon-stub"><slot /></span>'
          }
        }
      }
    })

  it('does not render content when there are no active filters', () => {
    const wrapper = mountComponent([])

    expect(wrapper.find('.filter-texts').exists()).toBe(false)
  })

  it('renders the total count and all filter labels', () => {
    const wrapper = mountComponent(['North', 'South'])

    expect(wrapper.find('.sum').text()).toBe('12')
    expect(wrapper.text()).toContain('translated:commons.result_count')
    expect(wrapper.text()).toContain('North')
    expect(wrapper.text()).toContain('South')
  })

  it('emits the filter index when removing a single filter', async () => {
    const wrapper = mountComponent(['North', 'South'])

    await wrapper.find('.text .icon-stub').trigger('click')

    expect(wrapper.emitted('clearFilter')).toEqual([[0]])
  })

  it('emits an empty marker when clearing all filters without overflow', async () => {
    const wrapper = mountComponent(['North'])

    await wrapper.find('.clear-btn-inner').trigger('click')

    expect(wrapper.emitted('clearFilter')).toEqual([['empty']])
  })

  it('shows scroll controls for overflow and clamps horizontal scrolling', async () => {
    const wrapper = mountComponent(['North'])
    const container = wrapper.find('.filter-texts-container').element as HTMLDivElement

    Object.defineProperty(container, 'scrollWidth', { configurable: true, value: 160 })
    Object.defineProperty(container, 'offsetWidth', { configurable: true, value: 100 })
    Object.defineProperty(container, 'scrollLeft', { configurable: true, writable: true, value: 0 })

    await wrapper.setProps({ filterTexts: ['North', 'South'] })
    await nextTick()
    await nextTick()

    expect(wrapper.find('.arrow-left').exists()).toBe(true)
    expect(wrapper.find('.arrow-right').exists()).toBe(true)

    for (let index = 0; index < 7; index++) {
      await wrapper.find('.arrow-right').trigger('click')
    }
    expect(container.scrollLeft).toBe(60)

    for (let index = 0; index < 7; index++) {
      await wrapper.find('.arrow-left').trigger('click')
    }
    expect(container.scrollLeft).toBe(0)
  })
})
