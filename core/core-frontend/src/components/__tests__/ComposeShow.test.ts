import { ref } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const composeState = vi.hoisted(() => ({
  areaData: null as any
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

import ComposeShow from '@/components/data-visualization/canvas/ComposeShow.vue'

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
    // ref already imported at top
    composeState.areaData = ref({ components: [] as any[] })
    composeState.areaData.value.components = []
  })

  it('shows the compose overlay only when element is selected', () => {
    composeState.areaData.value.components = [baseElement]
    const wrapper = mountComponent()

    expect(wrapper.find('.compose-shadow').exists()).toBe(true)
  })

  it('adds border class when showBorder is enabled', () => {
    composeState.areaData.value.components = [baseElement]
    const wrapper = mountComponent({ showBorder: true })

    expect(wrapper.get('.compose-shadow').classes()).toContain('shadow-border')
  })

  it('removes non-group element from selected area on mousedown', async () => {
    composeState.areaData.value.components = [baseElement]
    const wrapper = mountComponent()
    const stopPropagation = vi.fn()

    await wrapper.get('.compose-shadow').trigger('mousedown', { buttons: 1, stopPropagation })

    expect(composeState.areaData.value.components).toEqual([])
    expect(stopPropagation).toHaveBeenCalled()
  })
})
