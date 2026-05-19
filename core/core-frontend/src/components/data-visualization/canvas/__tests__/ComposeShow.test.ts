import { ref } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const composeState = vi.hoisted(() => ({
  areaData: null as ReturnType<typeof ref<any>>
}))

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: (store: Record<string, unknown>) => store
}))

vi.mock('@/store/modules/data-visualization/compose', () => ({
  composeStoreWithOut: () => ({
    areaData: composeState.areaData
  })
}))

import ComposeShow from '../ComposeShow.vue'

const baseElement = { id: 'view-1', component: 'Chart' }

const mountComponent = (props: Record<string, unknown> = {}) =>
  shallowMount(ComposeShow, {
    props: {
      element: baseElement,
      ...props
    }
  })

describe('ComposeShow', () => {
  beforeEach(() => {
    composeState.areaData = ref({ components: [] as Array<Record<string, unknown>> })
  })

  it('renders nothing when the element is not selected', () => {
    const wrapper = mountComponent()

    expect(wrapper.html()).toBe('<!--v-if-->')
  })

  it('shows the overlay with border when the element is selected', () => {
    composeState.areaData.value.components = [baseElement]
    const wrapper = mountComponent()

    expect(wrapper.get('.compose-shadow').classes()).toContain('shadow-border')
  })

  it('removes a selected non-group element on left mousedown', async () => {
    composeState.areaData.value.components = [baseElement]
    const wrapper = mountComponent()
    const stopPropagation = vi.fn()

    await wrapper.get('.compose-shadow').trigger('mousedown', { buttons: 1, stopPropagation })

    expect(composeState.areaData.value.components).toEqual([])
    expect(stopPropagation).toHaveBeenCalled()
  })

  it('keeps the selection on right click', async () => {
    composeState.areaData.value.components = [baseElement]
    const wrapper = mountComponent()
    const stopPropagation = vi.fn()

    await wrapper.get('.compose-shadow').trigger('mousedown', { buttons: 2, stopPropagation })

    expect(composeState.areaData.value.components).toEqual([baseElement])
    expect(stopPropagation).not.toHaveBeenCalled()
  })
})
