import { nextTick } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({ useI18n: () => ({ t: (key: string) => key }) }))

import QuotaFilterEditor from '../QuotaFilterEditor.vue'

const globalStubs = {
  ElSelect: { props: ['modelValue'], template: '<select class="select-stub"><slot /></select>' },
  ElOption: {
    props: ['label', 'value'],
    template: '<option class="option-stub" :value="value">{{ label }}</option>'
  },
  ElOptionGroup: {
    props: ['label'],
    template: '<optgroup class="option-group-stub"><slot /></optgroup>'
  },
  ElInput: { props: ['modelValue'], template: '<input class="input-stub" />' },
  ElButton: { template: '<button class="button-stub"><slot /></button>' },
  ElIcon: { template: '<i class="icon-stub"><slot /></i>' },
  Icon: { template: '<span class="vant-icon-stub"><slot /></span>' }
}

const createItem = () => ({
  name: 'Revenue',
  summary: 'sum',
  logic: 'and',
  filter: [{ term: 'eq', value: '100' }]
})

const mountComponent = (item = createItem()) =>
  shallowMount(QuotaFilterEditor, {
    props: { item },
    global: {
      stubs: globalStubs
    }
  })

describe('QuotaFilterEditor', () => {
  it('renders the field name, summary, and keeps the initial logic in state', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('Revenue')
    expect(wrapper.text()).toContain('chart.sum')
    expect((wrapper.vm as any).state.logic).toBe('and')
  })

  it('adds a default eq filter entry', () => {
    const item = createItem()
    const wrapper = mountComponent(item)

    ;(wrapper.vm as any).addFilter()

    expect(item.filter).toEqual([
      { term: 'eq', value: '100' },
      { term: 'eq', value: '' }
    ])
  })

  it('removes a filter by index', () => {
    const item = createItem()
    item.filter.push({ term: 'gt', value: '200' })
    const wrapper = mountComponent(item)

    ;(wrapper.vm as any).removeFilter(0)

    expect(item.filter).toEqual([{ term: 'gt', value: '200' }])
  })

  it('updates logic and hides the value input for null-based terms', async () => {
    const item = createItem()
    const wrapper = mountComponent(item)

    ;(wrapper.vm as any).logicChange('or')
    await wrapper.setProps({
      item: {
        ...item,
        filter: [{ term: 'not_null', value: '' }]
      }
    })
    await nextTick()

    expect(item.logic).toBe('or')
    expect(wrapper.find('.input-stub').exists()).toBe(false)
  })
})
