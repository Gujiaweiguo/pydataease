import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => key
  })
}))

import ChartError from '../ChartError.vue'

const globalStubs = {
  ElDialog: {
    props: ['modelValue'],
    template: '<div v-if="modelValue" class="dialog-stub"><slot /><slot name="footer" /></div>'
  },
  ElMain: { template: '<main class="main-stub"><slot /></main>' },
  ElButton: {
    emits: ['click'],
    template: '<button class="button-stub" @click="$emit(\'click\')"><slot /></button>'
  }
}

const mountComponent = (errMsg = 'Stack trace<br>line 2') =>
  shallowMount(ChartError, {
    props: { errMsg },
    global: {
      stubs: globalStubs
    }
  })

describe('ChartError', () => {
  it('renders guidance text and keeps the dialog hidden initially', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('chart.chart_error_tips')
    expect(wrapper.text()).toContain('chart.chart_show_error_info')
    expect(wrapper.find('.dialog-stub').exists()).toBe(false)
  })

  it('opens the dialog and renders the html error message when clicked', async () => {
    const wrapper = mountComponent('Render failed<br>series[0] is undefined')

    await wrapper.get('a').trigger('click')

    expect(wrapper.get('.dialog-stub').html()).toContain('Render failed')
    expect(wrapper.get('.dialog-stub').html()).toContain('<br>')
  })

  it('closes the dialog from the footer button', async () => {
    const wrapper = mountComponent()

    await wrapper.get('a').trigger('click')
    await wrapper.get('.button-stub').trigger('click')

    expect(wrapper.find('.dialog-stub').exists()).toBe(false)
  })
})
