import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const {
  curComponent,
  curComponentIndex,
  emitMock,
  getComponentByIdMock,
  getCurInfoMock,
  pausedMock,
  resumeMock
} = vi.hoisted(() => ({
  curComponent: { value: { id: 'current-component' } },
  curComponentIndex: { value: 0 },
  emitMock: vi.fn(),
  getComponentByIdMock: vi.fn(),
  getCurInfoMock: vi.fn(),
  pausedMock: vi.fn(),
  resumeMock: vi.fn()
}))

vi.mock('pinia', async () => {
  const actual = await vi.importActual<typeof import('pinia')>('pinia')
  return {
    ...actual,
    storeToRefs: () => ({
      curComponentIndex,
      curComponent
    })
  }
})

vi.mock('../dvMain', () => ({
  dvMainStoreWithOut: () => ({
    curComponentIndex,
    curComponent
  })
}))

vi.mock('../common', () => ({
  getCurInfo: getCurInfoMock,
  getComponentById: getComponentByIdMock
}))

vi.mock('@/utils/utils', () => ({
  swap: (list: any[], from: number, to: number) => {
    ;[list[from], list[to]] = [list[to], list[from]]
  }
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: () => ({ emitter: { emit: emitMock } })
}))

vi.mock('@/views/chart/components/js/g2plot_tooltip_carousel', () => ({
  default: {
    paused: pausedMock,
    resume: resumeMock
  }
}))

import { layerStore } from '../layer'

describe('layerStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.useFakeTimers()
    curComponent.value = { id: 'current-component' }
    curComponentIndex.value = 0
  })

  it('moves a component one layer up and updates the active index', () => {
    const componentData = [{ id: 'a' }, { id: 'b' }, { id: 'c' }]
    getCurInfoMock.mockReturnValue({ index: 1, componentData, targetComponent: componentData[1] })

    layerStore().upComponent('b')

    expect(componentData.map(item => item.id)).toEqual(['a', 'c', 'b'])
    expect(curComponentIndex.value).toBe(2)
  })

  it('moves a component down unless it is already at the bottom', () => {
    const componentData = [{ id: 'a' }, { id: 'b' }, { id: 'c' }]
    getCurInfoMock.mockReturnValueOnce({ index: 1, componentData, targetComponent: componentData[1] })

    layerStore().downComponent('b')

    expect(componentData.map(item => item.id)).toEqual(['b', 'a', 'c'])
    expect(curComponentIndex.value).toBe(0)

    getCurInfoMock.mockReturnValueOnce({ index: 0, componentData, targetComponent: componentData[0] })
    layerStore().downComponent('b')
    expect(componentData.map(item => item.id)).toEqual(['b', 'a', 'c'])
  })

  it('moves components to the top and bottom of the layer stack', () => {
    const componentData = [{ id: 'a' }, { id: 'b' }, { id: 'c' }]
    const store = layerStore()

    getCurInfoMock.mockReturnValueOnce({ index: 1, componentData, targetComponent: componentData[1] })
    store.topComponent('b')
    expect(componentData.map(item => item.id)).toEqual(['a', 'c', 'b'])
    expect(curComponentIndex.value).toBe(2)

    getCurInfoMock.mockReturnValueOnce({ index: 1, componentData, targetComponent: componentData[1] })
    store.bottomComponent('c')
    expect(componentData.map(item => item.id)).toEqual(['c', 'a', 'b'])
    expect(curComponentIndex.value).toBe(0)
  })

  it('hides and shows normal components directly', () => {
    const component = { id: 'table-1', isShow: false, innerType: 'table-basic' }
    getComponentByIdMock.mockReturnValue(component)

    const store = layerStore()
    store.showComponent('table-1')
    vi.runAllTimers()
    store.hideComponent('table-1')

    expect(component.isShow).toBe(false)
    expect(emitMock).toHaveBeenCalledWith('renderChart-current-component')
  })

  it('shows grouped table and map components and emits render events for each child', () => {
    const component = {
      id: 'group-1',
      component: 'Group',
      isShow: false,
      propValue: [
        { id: 'child-table', innerType: 'table-detail' },
        { id: 'child-map', innerType: 'map-heat' },
        { id: 'child-text', innerType: 'text' }
      ]
    }
    getComponentByIdMock.mockReturnValue(component)

    layerStore().showComponent('group-1')
    vi.runAllTimers()

    expect(component.isShow).toBe(true)
    expect(emitMock).toHaveBeenCalledWith('renderChart-child-table')
    expect(emitMock).toHaveBeenCalledWith('renderChart-child-map')
  })

  it('delegates tooltip carousel pause and resume calls only for existing components', () => {
    getComponentByIdMock.mockReturnValue({ id: 'chart-1' })
    const store = layerStore()

    store.pausedTooltipCarousel('chart-1')
    store.resumeTooltipCarousel('chart-1')

    expect(pausedMock).toHaveBeenCalledWith('chart-1')
    expect(resumeMock).toHaveBeenCalledWith('chart-1')
  })
})
