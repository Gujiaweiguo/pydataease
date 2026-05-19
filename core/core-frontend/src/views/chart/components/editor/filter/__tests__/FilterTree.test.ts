import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

const { errorMock } = vi.hoisted(() => ({
  errorMock: vi.fn()
}))

vi.mock('element-plus-secondary', async importOriginal => {
  const actual: Record<string, unknown> = (await importOriginal()) as Record<string, unknown>
  return {
    ...actual,
    ElMessage: { error: errorMock }
  }
})

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: vi.fn()
  })
}))

vi.mock('@/views/chart/components/editor/filter/auth-tree-chart/RowAuth.vue', () => ({
  default: {
    name: 'RowAuth',
    template: '<div class="row-auth-stub" />',
    methods: { init: () => undefined }
  }
}))

import FilterTree from '../FilterTree.vue'

const globalStubs = {
  ElDialog: {
    props: ['modelValue'],
    template: '<div v-if="modelValue" class="dialog-stub"><slot /><slot name="footer" /></div>'
  },
  ElButton: { template: '<button class="button-stub"><slot /></button>' },
  RowAuth: {
    name: 'RowAuth',
    template: '<div class="row-auth-stub" />',
    methods: { init: () => undefined }
  }
}

const filedList = () => [
  { id: 'f1', name: 'Field 1' },
  { id: 'f2', name: 'Field 2' },
  { id: '-1', name: 'Placeholder' }
]

const mountComponent = () =>
  shallowMount(FilterTree, {
    global: {
      stubs: globalStubs,
      provide: {
        filedList
      },
      mocks: {
        $t: (key: string) => key
      }
    }
  })

describe('FilterTree', () => {
  it('has dialog hidden by default', () => {
    const wrapper = mountComponent()

    expect(wrapper.find('.dialog-stub').exists()).toBe(false)
  })

  it('opens the dialog when init is called with a tree', async () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.init({ logic: 'and', items: [] })
    await wrapper.vm.$nextTick()

    expect(vm.dialogVisible).toBe(true)
    expect(wrapper.find('.dialog-stub').exists()).toBe(true)
  })

  it('computes filedList excluding items with id -1', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    const computed = vm.computedFiledList
    expect(Object.keys(computed)).toEqual(['f1', 'f2'])
    expect(computed['f1']).toEqual({ id: 'f1', name: 'Field 1' })
  })

  it('closes the dialog when closeFilter is called', async () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.dialogVisible = true
    vm.closeFilter()

    expect(vm.dialogVisible).toBe(false)
  })

  it('shows error message when changeFilter receives an errorMessage', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any

    vm.changeFilter({ logic: 'and', items: [], errorMessage: 'Something went wrong' })

    expect(errorMock).toHaveBeenCalledWith({
      message: 'Something went wrong',
      type: 'error',
      showClose: true
    })
  })

  it('emits filter-data and closes dialog on valid filter submission', () => {
    const wrapper = mountComponent()
    const vm = wrapper.vm as any
    vm.dialogVisible = true

    const items = [{ fieldId: 'f1', term: 'eq', value: '10' }]
    vm.changeFilter({ logic: 'and', items })

    expect(wrapper.emitted('filter-data')).toEqual([[{ logic: 'and', items }]])
    expect(vm.dialogVisible).toBe(false)
  })
})
