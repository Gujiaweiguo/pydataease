import { defineComponent, nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const storeMock = vi.hoisted(() => ({
  getViewIdList: [] as string[],
  add: vi.fn(),
  remove: vi.fn()
}))

vi.mock('@/store/modules/data-visualization/viewSelector', () => ({
  useViewSelectorStoreWithOut: () => storeMock
}))

import ComponentSelector from '@/components/visualization/ComponentSelector.vue'

const wrapperFactory = (resourceId = 'view-1') =>
  mount(ComponentSelector, {
    props: { resourceId },
    global: {
      stubs: {
        ElCheckbox: defineComponent({
          name: 'ElCheckbox',
          props: ['modelValue'],
          emits: ['update:modelValue', 'change'],
          template:
            '<input class="checkbox-stub" type="checkbox" :checked="modelValue" @change="$emit(\'update:modelValue\', $event.target.checked); $emit(\'change\', $event.target.checked)" />'
        })
      }
    }
  })

describe('ComponentSelector', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    storeMock.getViewIdList = []
  })

  it('starts checked when resourceId is already selected', () => {
    storeMock.getViewIdList = ['view-1']
    const wrapper = wrapperFactory()

    return nextTick().then(() => {
      expect((wrapper.get('.checkbox-stub').element as HTMLInputElement).checked).toBe(true)
    })
  })

  it('adds the resource id when checked', async () => {
    const wrapper = wrapperFactory()

    await nextTick()
    await wrapper.get('.checkbox-stub').setValue(true)

    expect(storeMock.add).toHaveBeenCalledWith('view-1')
  })

  it('removes the resource id when unchecked', async () => {
    storeMock.getViewIdList = ['view-1']
    const wrapper = wrapperFactory()

    await nextTick()
    await wrapper.get('.checkbox-stub').setValue(false)

    expect(storeMock.remove).toHaveBeenCalledWith('view-1')
  })
})
