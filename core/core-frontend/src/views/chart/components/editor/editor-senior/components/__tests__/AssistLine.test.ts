import { nextTick } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/config/axios', () => ({}))

const { errorMock } = vi.hoisted(() => ({
  errorMock: vi.fn()
}))

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (key: string) => key }) }))

vi.mock('element-plus-secondary', () => ({
  ElIcon: { name: 'ElIcon', template: '<i class="icon-stub"><slot /></i>' },
  ElMessage: { error: errorMock }
}))

import AssistLine from '../AssistLine.vue'

const globalStubs = {
  AssistLineEdit: { template: '<div class="assist-line-edit-stub" />' },
  ElRow: { template: '<div class="row-stub"><slot /></div>' },
  ElCol: { template: '<div class="col-stub"><slot /></div>' },
  ElDialog: {
    props: ['modelValue'],
    template:
      '<div v-if="modelValue" class="dialog-stub"><slot /><slot name="header" /><slot name="footer" /></div>'
  },
  ElButton: { template: '<button class="button-stub"><slot /></button>' },
  ElTooltip: { template: '<div class="tooltip-stub"><slot /><slot name="content" /></div>' },
  Icon: { template: '<span class="vant-icon-stub"><slot /></span>' }
}

const createChart = (assistLineCfg?: Record<string, unknown>) => ({
  type: 'bar',
  senior: {
    assistLineCfg: {
      enable: true,
      assistLine: [],
      ...assistLineCfg
    }
  }
})

const mountComponent = (
  chart = createChart(),
  quotaData = [{ id: 'field-1', name: 'Sales', summary: 'sum' }],
  quotaExtData = []
) =>
  shallowMount(AssistLine, {
    props: {
      chart,
      quotaData,
      quotaExtData,
      themes: 'dark',
      propertyInner: []
    },
    global: {
      stubs: globalStubs
    }
  })

describe('AssistLine', () => {
  it('adds a default fontSize during initialization when a line is missing one', () => {
    const wrapper = mountComponent(
      createChart({
        assistLine: [{ name: 'Target', field: '0', value: '10' }]
      })
    )

    expect((wrapper.vm as any).state.assistLineCfg.assistLine[0].fontSize).toBe(10)
  })

  it('shows an invalid field label when a dynamic line no longer matches available fields', () => {
    const wrapper = mountComponent(
      createChart({
        assistLine: [
          {
            name: 'Broken',
            field: '1',
            fieldId: 'missing',
            summary: 'sum',
            curField: { id: 'missing', name: 'Missing field' }
          }
        ]
      })
    )

    const vm = wrapper.vm as any
    const line = vm.state.assistLineCfg.assistLine[0]
    expect(line.field).toBe('1')
    expect(line.curField.id).toBe('missing')
    expect(vm.existField(line.curField)).toBe(false)
  })

  it('reports a validation error when a line name is missing', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.state.lineArr = [{ name: '', field: '0', value: '8' }]
    vm.changeLine()

    expect(errorMock).toHaveBeenCalledWith('chart.name_can_not_empty')
    expect(wrapper.emitted('onAssistLineChange')).toBeUndefined()
  })

  it('emits requestData for valid dynamic assist lines and closes the dialog', async () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.state.editLineDialog = true
    vm.state.lineArr = [
      {
        name: 'Dynamic target',
        field: '1',
        fieldId: 'field-1',
        summary: 'sum',
        curField: { id: 'field-1', name: 'Sales' }
      }
    ]
    vm.changeLine()
    await nextTick()

    expect(wrapper.emitted('onAssistLineChange')).toEqual([
      [
        {
          data: vm.state.assistLineCfg,
          requestData: true
        }
      ]
    ])
    expect(vm.state.editLineDialog).toBe(false)
  })
})
