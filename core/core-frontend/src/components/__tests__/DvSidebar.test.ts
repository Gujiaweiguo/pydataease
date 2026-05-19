import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const mockState = vi.hoisted(() => ({
  warning: vi.fn(),
  recordSnapshotCache: vi.fn()
}))

const dvMainRefs = vi.hoisted(() => ({
  canvasCollapse: null as any
}))

vi.mock('@/assets/svg/dv-info.svg', () => ({
  default: defineComponent({
    name: 'DvInfoSvg',
    template: '<svg class="dv-info-svg"></svg>'
  })
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => `t:${key}` })
}))

vi.mock('pinia', () => ({
  defineStore: () => () => ({}),
  createPinia: () => ({}),
  storeToRefs: (store: Record<string, unknown>) => store
}))

vi.mock('@/store/modules/data-visualization/dvMain', async () => {
  const { ref } = await import('vue')
  const canvasCollapse = ref({ defaultSide: false, rightSide: false })
  dvMainRefs.canvasCollapse = canvasCollapse

  return {
    dvMainStoreWithOut: () => ({
      canvasCollapse
    })
  }
})

vi.mock('@/store/modules/data-visualization/snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: mockState.recordSnapshotCache
  })
}))

vi.mock('element-plus-secondary', () => ({
  ElIcon: defineComponent({
    name: 'ElIcon',
    emits: ['click'],
    template: '<button class="el-icon-stub" @click="$emit(\'click\')"><slot /></button>'
  }),
  ElMessage: {
    warning: mockState.warning
  }
}))

import DvSidebar from '@/components/visualization/DvSidebar.vue'

const mountComponent = (props: Record<string, unknown> = {}) => {
  const element = props.element || { id: 'component-1', name: 'Old Name', label: 'Old Name' }

  return mount(DvSidebar, {
    props: {
      title: 'Sidebar Title',
      sideName: 'defaultSide',
      element,
      ...props
    },
    global: {
      stubs: {
        ElRow: defineComponent({
          name: 'ElRow',
          template: '<div class="row-stub"><slot /></div>'
        }),
        ElScrollbar: defineComponent({
          name: 'ElScrollbar',
          template: '<div class="scrollbar-stub"><slot /></div>'
        }),
        ElPopover: defineComponent({
          name: 'ElPopover',
          template:
            '<div class="popover-stub"><div class="popover-reference"><slot name="reference" /></div><div class="popover-content"><slot /></div></div>'
        }),
        Icon: defineComponent({
          name: 'Icon',
          template: '<span class="icon-stub"><slot /></span>'
        }),
        Expand: defineComponent({ name: 'Expand', template: '<svg class="expand-icon"></svg>' }),
        Fold: defineComponent({ name: 'Fold', template: '<svg class="fold-icon"></svg>' }),
        Teleport: defineComponent({
          name: 'Teleport',
          template: '<div class="teleport-stub"><slot /></div>'
        })
      }
    },
    slots: {
      default: '<div class="sidebar-slot">Slot Content</div>'
    }
  })
}

describe('DvSidebar', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    dvMainRefs.canvasCollapse.value = { defaultSide: false, rightSide: false }
  })

  it('renders the title and slot content while expanded', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('Sidebar Title')
    expect(wrapper.find('.sidebar-slot').exists()).toBe(true)
  })

  it('toggles into the collapsed state when the collapse icon is clicked', async () => {
    const wrapper = mountComponent()

    await wrapper.findAll('.el-icon-stub')[1].trigger('click')

    expect(dvMainRefs.canvasCollapse.value.defaultSide).toBe(true)
    expect(wrapper.find('.collapse-title').exists()).toBe(true)
    expect(wrapper.find('.main-content').exists()).toBe(false)
  })

  it('renames the current element when editing finishes with a valid value', async () => {
    const element = { id: 'component-1', name: 'Old Name', label: 'Old Name' }
    const wrapper = mountComponent({ element })

    await wrapper.get('.name-area-attr').trigger('dblclick')
    const input = wrapper.get('input')
    await input.setValue('New Name')
    await input.trigger('change')
    await input.trigger('blur')

    expect(mockState.recordSnapshotCache).toHaveBeenCalledWith('onComponentNameChange')
    expect(element.name).toBe('New Name')
    expect(element.label).toBe('New Name')
  })

  it('renames the view title for picture-group views', async () => {
    const view = { id: 'view-1', type: 'picture-group', title: 'Gallery' }
    const wrapper = mountComponent({
      view,
      title: 'Ignored Title',
      element: { id: 'view-1', name: 'Gallery', label: 'Gallery' }
    })

    await wrapper.get('.name-area-attr').trigger('dblclick')
    const input = wrapper.get('input')
    await input.setValue('New Gallery')
    await input.trigger('blur')

    expect(view.title).toBe('New Gallery')
  })
})
