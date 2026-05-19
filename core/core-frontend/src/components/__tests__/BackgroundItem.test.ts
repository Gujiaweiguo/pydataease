import { defineComponent } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const utilMock = vi.hoisted(() => ({
  hexColorToRGBA: vi.fn(() => 'rgba(0, 0, 0, 0.5)')
}))

const dvMainRefs = vi.hoisted(() => ({
  curComponent: null as any
}))

vi.mock('pinia', () => ({
  storeToRefs: (store: Record<string, unknown>) => store
}))

vi.mock('@/views/chart/components/js/util', () => ({
  hexColorToRGBA: utilMock.hexColorToRGBA
}))

vi.mock('@/components/icon-group/board-list', () => ({
  iconBoardMap: {
    star: defineComponent({
      name: 'StarBoard',
      template: '<svg class="star-board"></svg>'
    })
  }
}))

vi.mock('@/store/modules/data-visualization/dvMain', async () => {
  const { ref } = await import('vue')
  const curComponent = ref({
    commonBackground: {
      innerImage: 'board/star.svg',
      backgroundColorSelect: true,
      color: '#000000',
      alpha: 50,
      innerImageColor: '#ff0000'
    }
  })
  dvMainRefs.curComponent = curComponent

  return {
    dvMainStoreWithOut: () => ({
      curComponent
    })
  }
})

import BackgroundItem from '@/components/visualization/component-background/BackgroundItem.vue'

const mountComponent = () =>
  mount(BackgroundItem, {
    props: {
      template: {
        name: 'Star Template',
        url: 'board/star.svg'
      }
    },
    global: {
      stubs: {
        Icon: defineComponent({
          name: 'Icon',
          template: '<span class="icon-stub"><slot /></span>'
        })
      }
    }
  })

describe('BackgroundItem', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    dvMainRefs.curComponent.value = {
      commonBackground: {
        innerImage: 'board/star.svg',
        backgroundColorSelect: true,
        color: '#000000',
        alpha: 50,
        innerImageColor: '#ff0000'
      }
    }
  })

  it('renders the template name and active state', () => {
    const wrapper = mountComponent()

    expect(wrapper.text()).toContain('Star Template')
    expect(wrapper.find('.template-img').classes()).toContain('template-img-active')
  })

  it('applies the computed background color style when enabled', () => {
    const wrapper = mountComponent()

    expect(wrapper.get('.template-img').attributes('style')).toContain(
      'background-color: rgba(0, 0, 0, 0.5)'
    )
    expect(utilMock.hexColorToRGBA).toHaveBeenCalledWith('#000000', 50)
  })

  it('updates the selected background image when clicked', async () => {
    const wrapper = mountComponent()

    dvMainRefs.curComponent.value.commonBackground.innerImage = 'board/other.svg'
    await wrapper.get('.template-img').trigger('click')

    expect(dvMainRefs.curComponent.value.commonBackground.innerImage).toBe('board/star.svg')
  })
})
