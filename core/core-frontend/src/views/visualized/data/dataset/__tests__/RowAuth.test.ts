import { nextTick } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => `t:${key}` })
}))

vi.mock('../auth-tree/AuthTree.vue', () => ({
  default: {
    name: 'AuthTree',
    template: '<div class="auth-tree-stub" />'
  }
}))

import RowAuth from '../auth-tree/RowAuth.vue'

const mountComponent = () =>
  shallowMount(RowAuth, {
    global: {
      stubs: {
        AuthTree: true
      }
    }
  })

describe('RowAuth', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('initializes from an expression tree and emits a normalized payload on submit', async () => {
    const wrapper = mountComponent()

    ;(wrapper.vm as any).init({
      logic: 'and',
      items: [
        {
          enumValue: [],
          fieldId: 'field_1',
          field: { name: 'Region', deType: 0 },
          filterType: 'logic',
          subTree: null,
          term: 'eq',
          timeType: 'year',
          value: 'North'
        }
      ]
    })

    await nextTick()
    ;(wrapper.vm as any).submit()

    expect(wrapper.emitted('save')).toEqual([
      [
        {
          logic: 'and',
          items: [
            {
              enumValue: [],
              fieldId: 'field_1',
              filterType: 'logic',
              subTree: null,
              term: 'eq',
              timeType: 'year',
              type: 'item',
              value: 'North'
            }
          ],
          errorMessage: ''
        }
      ]
    ])
  })

  it('reports an error when a selected condition has no display name', async () => {
    const wrapper = mountComponent()

    ;(wrapper.vm as any).init({
      logic: 'or',
      items: [
        {
          enumValue: [],
          fieldId: 'field_1',
          field: { name: '', deType: 0 },
          filterType: 'logic',
          subTree: null,
          term: 'eq',
          timeType: 'year',
          value: 'North'
        }
      ]
    })

    await nextTick()
    ;(wrapper.vm as any).submit()

    expect((wrapper.emitted('save')?.[0]?.[0] as any).errorMessage).toBe(
      't:data_set.cannot_be_empty_'
    )
  })

  it('reports an error when enum filters have no values', async () => {
    const wrapper = mountComponent()

    ;(wrapper.vm as any).init({
      logic: 'or',
      items: [
        {
          enumValue: [],
          fieldId: 'field_2',
          field: { name: 'Role', deType: 0 },
          filterType: 'enum',
          subTree: null,
          term: 'in',
          timeType: 'year',
          value: ''
        }
      ]
    })

    await nextTick()
    ;(wrapper.vm as any).submit()

    expect((wrapper.emitted('save')?.[0]?.[0] as any).errorMessage).toBe(
      't:chart.enum_value_can_not_null'
    )
  })
})
