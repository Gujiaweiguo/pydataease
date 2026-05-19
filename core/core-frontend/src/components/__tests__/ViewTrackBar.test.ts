import { defineComponent, nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import ViewTrackBar from '../visualization/ViewTrackBar.vue'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => `translated:${key}` })
}))

const ElDropdownStub = defineComponent({
  name: 'ElDropdown',
  emits: ['visible-change'],
  template: '<div class="dropdown-stub"><slot /><slot name="dropdown" /></div>'
})

const ElDropdownMenuStub = defineComponent({
  name: 'ElDropdownMenu',
  template: '<div class="dropdown-menu-stub"><slot /></div>'
})

const ElDropdownItemStub = defineComponent({
  name: 'ElDropdownItem',
  emits: ['click', 'mousedown'],
  template:
    '<button class="dropdown-item-stub" @click="$emit(\'click\')" @mousedown="$emit(\'mousedown\', $event)"><slot /></button>'
})

describe('ViewTrackBar', () => {
  const mountComponent = () =>
    mount(ViewTrackBar, {
      props: {
        trackMenu: ['drill', 'jump'],
        fontFamily: 'serif'
      },
      global: {
        stubs: {
          ElDropdown: ElDropdownStub,
          ElDropdownMenu: ElDropdownMenuStub,
          ElDropdownItem: ElDropdownItemStub
        }
      }
    })

  const getExposedVm = (wrapper: ReturnType<typeof mountComponent>) =>
    wrapper.vm as unknown as { trackButtonClick: (id?: string) => void }

  it('renders translated menu items and applies the provided font family', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('translated:visualization.drill')
    expect(wrapper.text()).toContain('translated:visualization.jump')
    expect(wrapper.find('.dropdown-menu-stub').attributes('style')).toContain('font-family: serif;')
  })

  it('emits the clicked track action', async () => {
    const wrapper = mountComponent()

    await wrapper.findAll('.dropdown-item-stub')[1].trigger('click')

    expect(wrapper.emitted('trackClick')).toEqual([['jump']])
  })

  it('exposes trackButtonClick and forwards the click to the hidden input', () => {
    const wrapper = mountComponent()
    const input = wrapper.find('#input').element as HTMLInputElement
    const clickSpy = vi.spyOn(input, 'click')

    getExposedVm(wrapper).trackButtonClick('chart-9')

    expect(clickSpy).toHaveBeenCalledTimes(1)
  })

  it('hides matching tooltips when the dropdown visibility changes', async () => {
    const wrapper = mountComponent()
    const matchedTooltip = document.createElement('div')
    matchedTooltip.id = 'tooltip-chart-9'
    const otherTooltip = document.createElement('div')
    otherTooltip.id = 'tooltip-chart-1'
    matchedTooltip.className = 'g2-tooltip'
    otherTooltip.className = 'g2-tooltip'
    document.body.append(matchedTooltip, otherTooltip)

    getExposedVm(wrapper).trackButtonClick('chart-9')
    wrapper.findComponent(ElDropdownStub).vm.$emit('visible-change', true)
    await nextTick()

    expect(matchedTooltip.classList.contains('hidden-tooltip')).toBe(true)
    expect(otherTooltip.classList.contains('hidden-tooltip')).toBe(false)

    matchedTooltip.remove()
    otherTooltip.remove()
  })
})
