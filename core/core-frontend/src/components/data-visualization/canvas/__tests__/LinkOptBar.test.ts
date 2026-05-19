import { defineComponent, ref } from 'vue'
import { shallowMount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const routerState = vi.hoisted(() => ({
  currentRoute: null as any
}))

const emitterMock = vi.hoisted(() => ({
  emit: vi.fn()
}))

const dvMainState = vi.hoisted(() => ({
  fullscreenFlag: null as any
}))

const utilState = vi.hoisted(() => ({
  isMobile: vi.fn(() => false)
}))

vi.mock('@/router', () => ({
  default: routerState
}))

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: (store: Record<string, unknown>) => store
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({ emitter: emitterMock })
}))

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    fullscreenFlag: dvMainState.fullscreenFlag
  })
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({
    t: (key: string) => key
  })
}))

vi.mock('element-plus-secondary', () => ({
  ElIcon: defineComponent({
    name: 'ElIcon',
    emits: ['click'],
    template: '<button class="el-icon-stub" @click="$emit(\'click\')"><slot /></button>'
  })
}))

vi.mock('@/utils/utils', () => ({
  isMobile: utilState.isMobile
}))

import LinkOptBar from '../LinkOptBar.vue'

const stubs = {
  ElTooltip: defineComponent({
    name: 'ElTooltip',
    props: {
      content: {
        type: String,
        default: ''
      },
      disabled: {
        type: Boolean,
        default: false
      }
    },
    template: '<div class="el-tooltip-stub" :data-content="content"><slot /></div>'
  }),
  ElIcon: defineComponent({
    name: 'ElIcon',
    emits: ['click'],
    template: '<button class="el-icon-stub" @click="$emit(\'click\')"><slot /></button>'
  }),
  Icon: defineComponent({
    name: 'Icon',
    template: '<span class="icon-stub"><slot /></span>'
  })
}

const mountComponent = (props: Record<string, unknown> = {}) =>
  shallowMount(LinkOptBar, {
    props: {
      canvasStyleData: {
        dashboard: {
          themeColor: 'light'
        }
      },
      ...props
    },
    global: {
      stubs
    }
  })

const findIconByTooltip = (wrapper: ReturnType<typeof mountComponent>, content: string) =>
  wrapper.get(`.el-tooltip-stub[data-content="${content}"] .el-icon-stub`)

describe('LinkOptBar', () => {
  beforeEach(() => {
    // ref already imported at top
    vi.clearAllMocks()
    routerState.currentRoute = ref({ query: {} })
    dvMainState.fullscreenFlag = ref(false)
    utilState.isMobile.mockReturnValue(false)
    Object.defineProperty(document, 'fullscreenElement', {
      configurable: true,
      value: null
    })
    document.exitFullscreen = vi.fn().mockResolvedValue(undefined)
  })

  it('renders the light theme with the default compact width', () => {
    const wrapper = mountComponent()

    expect(wrapper.get('.link-bar-main').classes()).toContain('link-bar-main-light')
    expect(wrapper.get('.link-bar-main').attributes('style')).toContain('--fullWidth: 94px;')
  })

  it('renders dark theme and back action when opened from a link', () => {
    routerState.currentRoute.value = { query: { fromLink: 'true' } }
    const wrapper = mountComponent({
      canvasStyleData: {
        dashboard: {
          themeColor: 'dark'
        }
      }
    })

    expect(wrapper.get('.link-bar-main').classes()).toContain('link-bar-main-dark')
    expect(
      wrapper.find('.el-tooltip-stub[data-content="visualization.back_parent"]').exists()
    ).toBe(true)
  })

  it('toggles the active bar class when the first icon is clicked', async () => {
    const wrapper = mountComponent()

    await wrapper.findAll('.el-icon-stub')[0].trigger('click')

    expect(wrapper.get('.link-bar-main').classes()).toContain('link-bar-main-active')
  })

  it('emits canvasDownload when export is clicked', async () => {
    const wrapper = mountComponent()

    await findIconByTooltip(wrapper, 'visualization.export_pdf').trigger('click')

    expect(emitterMock.emit).toHaveBeenCalledWith('canvasDownload', 'pdf')
  })

  it('emits canvasFullscreen when entering fullscreen', async () => {
    const wrapper = mountComponent()

    await findIconByTooltip(wrapper, 'visualization.fullscreen').trigger('click')

    expect(emitterMock.emit).toHaveBeenCalledWith('canvasFullscreen')
  })

  it('calls document.exitFullscreen when already fullscreen', async () => {
    dvMainState.fullscreenFlag.value = true
    Object.defineProperty(document, 'fullscreenElement', {
      configurable: true,
      value: { id: 'full-screen-node' }
    })
    const wrapper = mountComponent()

    await findIconByTooltip(wrapper, 'visualization.ext_fullscreen').trigger('click')

    expect(document.exitFullscreen).toHaveBeenCalled()
  })
})
