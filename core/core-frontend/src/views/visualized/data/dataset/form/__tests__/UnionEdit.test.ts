import { defineComponent, ref } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (k: string) => k })
}))

vi.mock('@/config/axios', () => ({}))

vi.mock('@/api/dataset', () => ({
  getTableField: vi.fn()
}))

import UnionEdit from '../UnionEdit.vue'

const globalStubs = {
  UnionFieldList: { template: '<div class="union-field-list-stub"><slot /></div>' },
  UnionItemEdit: { template: '<div class="union-item-edit-stub"><slot /></div>' }
}

describe('UnionEdit', () => {
  const provideDefaults = () => ({
    isCross: ref(false)
  })

  it('renders without errors', () => {
    const wrapper = shallowMount(UnionEdit, {
      props: { editArr: [] },
      global: {
        stubs: globalStubs,
        provide: provideDefaults()
      }
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('exposes clearState method', () => {
    const wrapper = shallowMount(UnionEdit, {
      props: { editArr: [] },
      global: {
        stubs: globalStubs,
        provide: provideDefaults()
      }
    })
    expect(typeof (wrapper.vm as any).clearState).toBe('function')
  })

  it('exposes initState method', () => {
    const wrapper = shallowMount(UnionEdit, {
      props: { editArr: [] },
      global: {
        stubs: globalStubs,
        provide: provideDefaults()
      }
    })
    expect(typeof (wrapper.vm as any).initState).toBe('function')
  })

  it('exposes node and parent reactive objects', () => {
    const wrapper = shallowMount(UnionEdit, {
      props: { editArr: [] },
      global: {
        stubs: globalStubs,
        provide: provideDefaults()
      }
    })
    expect((wrapper.vm as any).node).toBeDefined()
    expect((wrapper.vm as any).parent).toBeDefined()
  })
})
