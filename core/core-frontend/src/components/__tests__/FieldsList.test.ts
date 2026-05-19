import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const emitterEmit = vi.hoisted(() => vi.fn())

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({ emitter: { emit: emitterEmit } })
}))

import FieldsList from '@/components/visualization/FieldsList.vue'

const mountComponent = () =>
  mount(FieldsList, {
    props: {
      element: { id: 'chart-1' },
      fields: [
        { id: 'field-1', name: 'Sales' },
        { id: 'field-2', name: 'Profit' }
      ]
    },
    global: {
      stubs: {
        ElButton: defineComponent({
          name: 'ElButton',
          emits: ['click'],
          template:
            '<button class="field-button" :title="$attrs.title" @click="$emit(\'click\')"><slot /></button>'
        })
      }
    }
  })

describe('FieldsList', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders every provided field as a button', () => {
    const wrapper = mountComponent()

    expect(wrapper.findAll('.field-button')).toHaveLength(2)
    expect(wrapper.text()).toContain('Sales')
    expect(wrapper.text()).toContain('Profit')
  })

  it('emits the selected field through the event bus', async () => {
    const wrapper = mountComponent()

    await wrapper.findAll('.field-button')[1].trigger('click')

    expect(emitterEmit).toHaveBeenCalledWith('fieldSelect-chart-1', {
      id: 'field-2',
      name: 'Profit'
    })
  })

  it('prevents the default mousedown action in the field area', async () => {
    const wrapper = mountComponent()
    const preventDefault = vi.fn()

    await wrapper.get('.field-main').trigger('mousedown', { preventDefault })

    expect(preventDefault).toHaveBeenCalled()
  })
})
