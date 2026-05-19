import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => key
  })
}))

import ChartError from '@/views/chart/components/views/components/ChartError.vue'

const ElDialogStub = defineComponent({
  name: 'ElDialog',
  props: {
    modelValue: {
      type: Boolean,
      default: false
    }
  },
  template:
    '<div v-if="modelValue" class="el-dialog-stub"><div class="dialog-body"><slot /></div><div class="dialog-footer"><slot name="footer" /></div></div>'
})

const ElMainStub = defineComponent({
  name: 'ElMain',
  template: '<main class="el-main-stub"><slot /></main>'
})

const ElButtonStub = defineComponent({
  name: 'ElButton',
  emits: ['click'],
  template: '<button class="el-button-stub" @click="$emit(\'click\')"><slot /></button>'
})

const mountChartError = (errMsg = 'Stack trace<br>line 2') =>
  mount(ChartError, {
    props: { errMsg },
    global: {
      stubs: {
        ElDialog: ElDialogStub,
        ElMain: ElMainStub,
        ElButton: ElButtonStub
      }
    }
  })

describe('ChartError', () => {
  it('renders translated error guidance before the dialog opens', () => {
    const wrapper = mountChartError()

    expect(wrapper.text()).toContain('chart.chart_error_tips')
    expect(wrapper.text()).toContain('chart.chart_show_error_info')
    expect(wrapper.find('.el-dialog-stub').exists()).toBe(false)
  })

  it('opens the dialog and renders the error html when the link is clicked', async () => {
    const wrapper = mountChartError('Render failed<br>series[0] is undefined')

    await wrapper.get('a').trigger('click')

    expect(wrapper.get('.el-dialog-stub').html()).toContain('Render failed')
    expect(wrapper.get('.el-dialog-stub').html()).toContain('<br>')
    expect(wrapper.text()).toContain('commons.close')
  })

  it('closes the dialog when the footer button is clicked', async () => {
    const wrapper = mountChartError()

    await wrapper.get('a').trigger('click')
    await wrapper.get('.el-button-stub').trigger('click')

    expect(wrapper.find('.el-dialog-stub').exists()).toBe(false)
  })
})
