import { nextTick } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (key: string) => key }) }))

import ScrollCfg from '../ScrollCfg.vue'

const globalStubs = {
  ElForm: {
    props: ['model', 'disabled'],
    template: '<form class="form-stub" :data-disabled="String(disabled)"><slot /></form>'
  },
  ElFormItem: {
    props: ['label'],
    template: '<div class="form-item-stub" :data-label="label"><slot /></div>'
  },
  ElInputNumber: {
    props: ['modelValue'],
    template: '<input class="input-number-stub" type="number" />'
  }
}

const createChart = (senior: unknown) => ({
  senior
})

const mountComponent = (
  chart = createChart({ scrollCfg: { open: true, row: 5, step: 2, interval: 1500 } })
) =>
  shallowMount(ScrollCfg, {
    props: {
      chart,
      themes: 'dark'
    },
    global: {
      stubs: globalStubs
    }
  })

describe('ScrollCfg', () => {
  it('initializes scrollForm from object-based senior config', () => {
    const wrapper = mountComponent()

    expect((wrapper.vm as any).state.scrollForm).toEqual({
      open: true,
      row: 5,
      step: 2,
      interval: 1500
    })
    expect(wrapper.get('.form-stub').attributes('data-disabled')).toBe('false')
  })

  it('parses string-based senior config', () => {
    const wrapper = mountComponent(
      createChart(JSON.stringify({ scrollCfg: { open: false, row: 8, step: 3, interval: 2400 } }))
    )

    expect((wrapper.vm as any).state.scrollForm).toEqual({
      open: false,
      row: 8,
      step: 3,
      interval: 2400
    })
  })

  it('emits the current scroll config when changeScrollCfg runs', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.state.scrollForm.interval = 3200
    vm.changeScrollCfg()

    expect(wrapper.emitted('onScrollCfgChange')).toEqual([[vm.state.scrollForm]])
  })

  it('updates state when the chart prop changes', async () => {
    const wrapper = mountComponent()

    await wrapper.setProps({
      chart: createChart({ scrollCfg: { open: false, row: 12, step: 4, interval: 5000 } })
    })
    await nextTick()

    expect((wrapper.vm as any).state.scrollForm).toEqual({
      open: false,
      row: 12,
      step: 4,
      interval: 5000
    })
    expect(wrapper.get('.form-stub').attributes('data-disabled')).toBe('true')
  })
})
