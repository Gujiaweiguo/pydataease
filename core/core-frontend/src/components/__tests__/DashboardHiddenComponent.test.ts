import { ref } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { state } = vi.hoisted(() => ({
  state: {
    canvasStyleData: null as any,
    canvasViewInfo: null as any,
    componentData: null as any,
    dvInfo: null as any
  }
}))

vi.mock('pinia', async () => {
  const actual = await vi.importActual<typeof import('pinia')>('pinia')
  return {
    ...actual,
    storeToRefs: (store: any) => store
  }
})

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({
    componentData: state.componentData,
    canvasStyleData: state.canvasStyleData,
    canvasViewInfo: state.canvasViewInfo,
    dvInfo: state.dvInfo
  })
}))

vi.mock('@/components/data-visualization/canvas/ComponentWrapper.vue', () => ({
  default: {
    name: 'ComponentWrapper',
    props: ['config', 'viewInfo', 'scale'],
    template:
      '<div class="component-wrapper-stub" :data-id="config.id" :data-scale="String(scale)">{{ viewInfo?.id }}</div>'
  }
}))

vi.mock('../empty-background/src/EmptyBackground.vue', () => ({
  default: {
    name: 'EmptyBackground',
    props: ['description', 'imgType'],
    template:
      '<div class="empty-background-stub" :data-description="description" :data-img-type="imgType"></div>'
  }
}))

vi.mock('../icon-custom/src/Icon.vue', () => ({
  default: {
    name: 'Icon',
    template: '<span class="custom-icon-stub"><slot /></span>'
  }
}))

import DashboardHiddenComponent from '../dashboard/DashboardHiddenComponent.vue'

describe('DashboardHiddenComponent', () => {
  const mountComponent = () =>
    mount(DashboardHiddenComponent, {
      global: {
        mocks: {
          $t: (key: string) => `translated:${key}`
        },
        stubs: {
          ElTooltip: {
            template: '<div class="tooltip-stub"><slot /></div>'
          },
          ElIcon: {
            template: '<i class="icon-stub"><slot /></i>'
          }
        }
      }
    })

  beforeEach(() => {
    state.componentData = ref([])
    state.canvasStyleData = ref({ scale: 100 })
    state.canvasViewInfo = ref({})
    state.dvInfo = ref({ type: 'dashboard' })
  })

  it('renders the empty state when there are no hidden components', () => {
    const wrapper = mountComponent()

    expect(wrapper.find('.empty-background-stub').attributes('data-description')).toBe(
      'translated:visualization.no_hidden_components'
    )
  })

  it('renders only dashboardHidden components and passes wrapper props', () => {
    state.componentData.value = [
      { id: 'hidden-1', dashboardHidden: true },
      { id: 'visible-1', dashboardHidden: false },
      { id: 'hidden-2', dashboardHidden: true }
    ]
    state.canvasViewInfo.value = {
      'hidden-1': { id: 'view-1' },
      'hidden-2': { id: 'view-2' }
    }

    const wrapper = mountComponent()
    const wrappers = wrapper.findAll('.component-wrapper-stub')

    expect(wrappers).toHaveLength(2)
    expect(wrappers[0].attributes('data-id')).toBe('hidden-1')
    expect(wrappers[0].attributes('data-scale')).toBe('100')
    expect(wrappers[0].text()).toContain('view-1')
  })

  it('restores a hidden component and emits cancelHidden', async () => {
    state.componentData.value = [{ id: 'hidden-1', dashboardHidden: true }]
    state.canvasViewInfo.value = { 'hidden-1': { id: 'view-1' } }

    const wrapper = mountComponent()

    await wrapper.find('.select-to-dashboard').trigger('click')

    expect(state.componentData.value[0].dashboardHidden).toBe(false)
    expect(wrapper.emitted('cancelHidden')).toEqual([[state.componentData.value[0]]])
  })
})
