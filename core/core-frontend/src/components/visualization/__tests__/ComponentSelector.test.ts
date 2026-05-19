import { defineComponent, nextTick } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mocks = vi.hoisted(() => ({
  getViewIdList: [] as string[],
  add: vi.fn(),
  remove: vi.fn()
}))

vi.mock('@/store/modules/data-visualization/viewSelector', () => ({
  useViewSelectorStoreWithOut: () => ({
    getViewIdList: mocks.getViewIdList,
    add: mocks.add,
    remove: mocks.remove
  })
}))

import ComponentSelector from '../ComponentSelector.vue'

const stubs = {
  ElCheckbox: defineComponent({
    name: 'ElCheckbox',
    props: ['modelValue'],
    emits: ['update:modelValue', 'change'],
    template:
      '<input class="checkbox-stub" type="checkbox" :checked="modelValue" @change="$emit(\'update:modelValue\', $event.target.checked); $emit(\'change\', $event.target.checked)" />'
  })
}

const mountComponent = (resourceId = 'view-1') =>
  shallowMount(ComponentSelector, {
    props: { resourceId },
    global: { stubs }
  })

describe('ComponentSelector', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mocks.getViewIdList = []
  })

  it('renders checkbox control', () => {
    const wrapper = mountComponent()

    expect(wrapper.find('.checkbox-stub').exists()).toBe(true)
  })

  it('initializes checked state from selected ids', async () => {
    mocks.getViewIdList = ['view-1']
    const wrapper = mountComponent('view-1')

    await nextTick()

    expect(wrapper.getComponent({ name: 'ElCheckbox' }).props('modelValue')).toBe(true)
  })

  it('adds resource id when checked', async () => {
    const wrapper = mountComponent('view-2')

    wrapper.getComponent({ name: 'ElCheckbox' }).vm.$emit('change', true)
    await nextTick()

    expect(mocks.add).toHaveBeenCalledWith('view-2')
  })

  it('removes resource id when unchecked', async () => {
    mocks.getViewIdList = ['view-3']
    const wrapper = mountComponent('view-3')

    await nextTick()
    wrapper.getComponent({ name: 'ElCheckbox' }).vm.$emit('change', false)
    await nextTick()

    expect(mocks.remove).toHaveBeenCalledWith('view-3')
  })
})
