import { ref } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const dvRefs = vi.hoisted(() => ({
  mousePointShadowMap: null as any,
  canvasStyleData: null as any
}))

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: (store: Record<string, unknown>) => store
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => dvRefs
}))

import PointShadow from '@/components/data-visualization/canvas/PointShadow.vue'

describe('PointShadow', () => {
  beforeEach(() => {
    // ref already imported at top
    dvRefs.mousePointShadowMap = ref({ mouseX: 200, mouseY: 120, width: 80, height: 40 })
    dvRefs.canvasStyleData = ref({ scale: 150 })
  })

  it('renders the drag-out tip text', () => {
    const wrapper = shallowMount(PointShadow, { props: { canvasId: 'canvas-main' } })

    expect(wrapper.text()).toContain('组件将被移出Tab')
  })

  it('computes wrapper position from mouse shadow map', () => {
    const wrapper = shallowMount(PointShadow, { props: { canvasId: 'canvas-main' } })
    const style = wrapper.get('.point-shadow').attributes('style')

    expect(style).toContain('left: 160px;')
    expect(style).toContain('top: 40px;')
    expect(style).toContain('width: 80px;')
    expect(style).toContain('height: 40px;')
  })

  it('scales the tip font size with canvas scale', () => {
    const wrapper = shallowMount(PointShadow, { props: { canvasId: 'canvas-main' } })

    expect(wrapper.get('.point-shadow-tips').attributes('style')).toContain('font-size: 24px;')
  })
})
