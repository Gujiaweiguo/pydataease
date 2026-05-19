import { defineComponent, nextTick } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

const elMessageError = vi.hoisted(() => vi.fn())

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => `t:${key}`
  })
}))

vi.mock('element-plus-secondary', () => ({
  ElMessage: {
    error: elMessageError
  }
}))

import Cron from '../cron/src/Cron.vue'

const SecondAndMinuteStub = defineComponent({
  name: 'SecondAndMinuteStub',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    label: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue'],
  template:
    '<div class="second-minute-stub" :data-label="label" :data-model-value="modelValue"></div>'
})

const HourStub = defineComponent({
  name: 'HourStub',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    label: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue'],
  template: '<div class="hour-stub" :data-label="label" :data-model-value="modelValue"></div>'
})

const DayStub = defineComponent({
  name: 'DayStub',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    label: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue'],
  template: '<div class="day-stub" :data-label="label" :data-model-value="modelValue"></div>'
})

const MonthStub = defineComponent({
  name: 'MonthStub',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    label: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue'],
  template: '<div class="month-stub" :data-label="label" :data-model-value="modelValue"></div>'
})

const WeekStub = defineComponent({
  name: 'WeekStub',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    label: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue'],
  template: '<div class="week-stub" :data-label="label" :data-model-value="modelValue"></div>'
})

const YearStub = defineComponent({
  name: 'YearStub',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    label: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue'],
  template: '<div class="year-stub" :data-label="label" :data-model-value="modelValue"></div>'
})

const ElTabsStub = defineComponent({
  name: 'ElTabs',
  props: {
    modelValue: {
      type: String,
      default: ''
    }
  },
  template: '<div class="el-tabs-stub" :data-model-value="modelValue"><slot /></div>'
})

const ElTabPaneStub = defineComponent({
  name: 'ElTabPane',
  props: {
    label: {
      type: String,
      default: ''
    },
    name: {
      type: String,
      default: ''
    }
  },
  template: '<section class="el-tab-pane-stub" :data-name="name">{{ label }}<slot /></section>'
})

const ElTableStub = defineComponent({
  name: 'ElTable',
  props: {
    data: {
      type: Array,
      default: () => []
    }
  },
  template: '<div class="el-table-stub" :data-length="String(data.length)"><slot /></div>'
})

const ElTableColumnStub = defineComponent({
  name: 'ElTableColumn',
  props: {
    prop: {
      type: String,
      default: ''
    },
    label: {
      type: String,
      default: ''
    }
  },
  template: '<div class="el-table-column-stub" :data-prop="prop" :data-label="label"></div>'
})

const mountComponent = (props?: Record<string, unknown>) =>
  shallowMount(Cron, {
    props: {
      modelValue: '* * * ? * 1 *',
      ...props
    },
    global: {
      stubs: {
        'second-and-minute': SecondAndMinuteStub,
        hour: HourStub,
        day: DayStub,
        month: MonthStub,
        week: WeekStub,
        year: YearStub,
        ElTabs: ElTabsStub,
        ElTabPane: ElTabPaneStub,
        ElTable: ElTableStub,
        ElTableColumn: ElTableColumnStub
      }
    }
  })

describe('Cron', () => {
  it('passes parsed cron values into each tab child and summary table', () => {
    const wrapper = mountComponent({ modelValue: '1 2 3 ? 5 6 2024' })

    const secondsAndMinutes = wrapper.findAll('.second-minute-stub')

    expect(secondsAndMinutes[0].attributes('data-model-value')).toBe('1')
    expect(secondsAndMinutes[1].attributes('data-model-value')).toBe('2')
    expect(wrapper.get('.hour-stub').attributes('data-model-value')).toBe('3')
    expect(wrapper.get('.day-stub').attributes('data-model-value')).toBe('?')
    expect(wrapper.get('.month-stub').attributes('data-model-value')).toBe('5')
    expect(wrapper.get('.week-stub').attributes('data-model-value')).toBe('6')
    expect(wrapper.get('.year-stub').attributes('data-model-value')).toBe('2024')
    expect(wrapper.findAll('.el-table-column-stub')).toHaveLength(7)
  })

  it('emits the rebuilt cron expression when a child section changes', async () => {
    const wrapper = mountComponent({ modelValue: '* * * ? * 1 *' })

    wrapper.getComponent(HourStub).vm.$emit('update:modelValue', '5-8')
    await nextTick()

    expect(wrapper.emitted('update:modelValue')?.at(-1)).toEqual(['* * 5-8 ? * 1 *'])
  })

  it('reports invalid day and week combinations through ElMessage', async () => {
    const wrapper = mountComponent({ modelValue: '* * * ? * 1 *' })

    wrapper.getComponent(WeekStub).vm.$emit('update:modelValue', '?')
    await nextTick()

    expect(elMessageError).toHaveBeenCalledWith('t:cron.d_w_cant_not_set')
  })
})
