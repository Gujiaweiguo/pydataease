import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const utilMock = vi.hoisted(() => ({
  isMainCanvas: vi.fn((canvasId: string) => canvasId === 'canvas-main'),
  isMobile: vi.fn(() => false)
}))

const dvMainRefs = vi.hoisted(() => ({
  fullscreenFlag: null as any,
  store: { mobileInPc: false }
}))

vi.mock('@/assets/svg/exit-fullscreen.svg', () => ({
  default: defineComponent({
    name: 'ExitFullscreenSvg',
    template: '<svg class="exit-svg"></svg>'
  })
}))

vi.mock('@/utils/canvasUtils', () => ({
  isMainCanvas: utilMock.isMainCanvas
}))

vi.mock('@/utils/utils', () => ({
  isMobile: utilMock.isMobile
}))

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: (store: Record<string, unknown>) => store
}))

vi.mock('@/store/modules/data-visualization/dvMain', async () => {
  const { ref } = await import('vue')
  const fullscreenFlag = ref(true)
  const store = dvMainRefs.store
  dvMainRefs.fullscreenFlag = fullscreenFlag

  return {
    dvMainStoreWithOut: () => ({
      ...store,
      fullscreenFlag
    })
  }
})

import CanvasExtFullscreenBar from '@/components/visualization/CanvasExtFullscreenBar.vue'

const mountComponent = (props: Record<string, unknown> = {}) =>
  mount(CanvasExtFullscreenBar, {
    props,
    global: {
      mocks: {
        $t: (key: string) => `t:${key}`
      },
      stubs: {
        ElButton: defineComponent({
          name: 'ElButton',
          emits: ['click'],
          template: '<button class="fullscreen-button" @click="$emit(\'click\')"><slot /></button>'
        }),
        ElIcon: defineComponent({
          name: 'ElIcon',
          template: '<span class="el-icon-stub"><slot /></span>'
        }),
        Icon: defineComponent({
          name: 'Icon',
          template: '<span class="icon-stub"><slot /></span>'
        })
      }
    }
  })

describe('CanvasExtFullscreenBar', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    dvMainRefs.fullscreenFlag.value = true
    dvMainRefs.store.mobileInPc = false
    document.exitFullscreen = vi.fn()
  })

  it('renders the exit fullscreen button for the main preview canvas', () => {
    const wrapper = mountComponent({ canvasId: 'canvas-main', showPosition: 'preview' })

    expect(wrapper.find('.bar-main-right').exists()).toBe(true)
    expect(wrapper.text()).toContain('t:visualization.ext_fullscreen')
  })

  it('hides the button when fullscreen mode should not be shown', () => {
    const nonMainWrapper = mountComponent({ canvasId: 'secondary-canvas', showPosition: 'preview' })
    dvMainRefs.store.mobileInPc = true
    const mobileWrapper = mountComponent({ canvasId: 'canvas-main', showPosition: 'preview' })

    expect(nonMainWrapper.html()).toBe('<!--v-if-->')
    expect(mobileWrapper.html()).toBe('<!--v-if-->')
  })

  it('prevents default mouse events on the toolbar container', async () => {
    const wrapper = mountComponent({ canvasId: 'canvas-main', showPosition: 'preview' })
    const preventDefault = vi.fn()
    const stopPropagation = vi.fn()

    await wrapper.get('.bar-main-right').trigger('mousedown', { preventDefault, stopPropagation })

    expect(preventDefault).toHaveBeenCalled()
    expect(stopPropagation).toHaveBeenCalled()
  })

  it('calls document.exitFullscreen when the button is clicked', async () => {
    const wrapper = mountComponent({ canvasId: 'canvas-main', showPosition: 'preview' })

    await wrapper.get('.fullscreen-button').trigger('click')

    expect(document.exitFullscreen).toHaveBeenCalled()
  })
})
