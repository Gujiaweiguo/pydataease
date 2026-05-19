import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const {
  adaptCurThemeCommonStyleMock,
  addComponentMock,
  addCopyComponentMock,
  canvasStyleData,
  componentData,
  composeStoreMock,
  contextmenuStoreMock,
  curComponent,
  curComponentIndex,
  curMultiplexingComponents,
  deleteComponentByIdMock,
  dvInfo,
  emitMock,
  generateIDMock,
  menuLeft,
  menuTop,
  multiplexingStyleAdapt,
  pcMatrixCount,
  recordSnapshotCacheMock,
  setAreaDataMock,
  setCurComponentMock,
  snapshotStoreMock
} = vi.hoisted(() => ({
  adaptCurThemeCommonStyleMock: vi.fn(),
  addComponentMock: vi.fn(),
  addCopyComponentMock: vi.fn(),
  canvasStyleData: { value: { scale: 100, width: 1920, height: 1080 } },
  componentData: { value: [] as any[] },
  composeStoreMock: { areaData: { components: [] as any[] }, setAreaData: vi.fn() },
  contextmenuStoreMock: { menuTop: { value: 120 }, menuLeft: { value: 240 } },
  curComponent: { value: null as any },
  curComponentIndex: { value: 0 },
  curMultiplexingComponents: { value: {} as Record<string, any> },
  deleteComponentByIdMock: vi.fn(),
  dvInfo: { value: { type: 'dataV' } },
  emitMock: vi.fn(),
  generateIDMock: vi.fn(),
  menuLeft: { value: 240 },
  menuTop: { value: 120 },
  multiplexingStyleAdapt: { value: true },
  pcMatrixCount: { value: { x: 72, y: 36 } },
  recordSnapshotCacheMock: vi.fn(),
  setAreaDataMock: vi.fn(),
  setCurComponentMock: vi.fn(),
  snapshotStoreMock: { recordSnapshotCache: vi.fn() }
}))

vi.mock('pinia', async () => {
  const actual = await vi.importActual<typeof import('pinia')>('pinia')
  return {
    ...actual,
    storeToRefs: (store: any) => store
  }
})

vi.mock('../dvMain', () => ({
  dvMainStoreWithOut: () => ({
    multiplexingStyleAdapt,
    curComponent,
    curComponentIndex,
    curMultiplexingComponents,
    dvInfo,
    pcMatrixCount,
    canvasStyleData,
    componentData,
    addCopyComponent: addCopyComponentMock,
    setCurComponent: setCurComponentMock,
    deleteComponentById: deleteComponentByIdMock,
    addComponent: addComponentMock
  })
}))

vi.mock('../contextmenu', () => ({
  contextmenuStoreWithOut: () => ({
    menuTop,
    menuLeft
  })
}))

vi.mock('../compose', () => ({
  composeStoreWithOut: () => ({
    areaData: composeStoreMock.areaData,
    setAreaData: setAreaDataMock
  })
}))

vi.mock('../snapshot', () => ({
  snapshotStoreWithOut: () => ({
    recordSnapshotCache: recordSnapshotCacheMock
  })
}))

vi.mock('@/utils/generateID', () => ({ generateID: generateIDMock }))
vi.mock('@/utils/utils', () => ({ deepCopy: <T>(value: T) => JSON.parse(JSON.stringify(value)) }))
vi.mock('@/utils/eventBus', () => ({ default: { emit: emitMock } }))
vi.mock('@/utils/canvasStyle', () => ({ adaptCurThemeCommonStyle: adaptCurThemeCommonStyleMock }))
vi.mock('@/utils/canvasUtils', () => ({ maxYComponentCount: () => 42 }))

import { copyStore } from '../copy'

describe('copyStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    vi.useFakeTimers()
    let idCounter = 0
    generateIDMock.mockImplementation(() => `generated-${++idCounter}`)
    curComponent.value = null
    curComponentIndex.value = 0
    dvInfo.value = { type: 'dataV' }
    componentData.value = []
    composeStoreMock.areaData.components = []
    addCopyComponentMock.mockImplementation((component: any) => {
      componentData.value.push(component)
    })
  })

  it('copies the current component when it is not a GroupArea', () => {
    curComponent.value = { id: 'component-1', component: 'Text', style: { top: 1, left: 2 } }

    const store = copyStore()
    store.copy()

    expect(store.copyData).toEqual({
      data: [{ id: 'component-1', component: 'Text', style: { top: 1, left: 2 } }],
      index: curComponentIndex
    })
    expect(store.copyData.data[0]).not.toBe(curComponent.value)
    expect(store.isCut).toBe(false)
  })

  it('copies selected area components when the current component is a GroupArea', () => {
    curComponent.value = { id: 'group-area', component: 'GroupArea' }
    composeStoreMock.areaData.components = [{ id: 'area-1', component: 'Text' }]

    const store = copyStore()
    store.copy()

    expect(store.copyData?.data).toEqual([{ id: 'area-1', component: 'Text' }])
  })

  it('pastes copied components into dataV canvases with new ids and offset positions', () => {
    const store = copyStore()
    store.copyData = {
      data: [
        {
          id: 'old-id',
          component: 'Text',
          canvasId: 'Group-old-group',
          style: { top: 5, left: 8, width: 10, height: 10 },
          y: 1,
          sizeY: 2
        }
      ],
      copyCanvasViewInfo: { copied: true },
      copyFrom: 'manual'
    } as any

    store.paste()
    vi.runAllTimers()

    expect(addCopyComponentMock).toHaveBeenCalledWith(
      expect.objectContaining({
        id: 'generated-1',
        canvasId: 'canvas-main',
        style: expect.objectContaining({ top: 15, left: 18 })
      }),
      { 'old-id': 'generated-1' },
      { copied: true }
    )
    expect(setCurComponentMock).toHaveBeenCalledWith({
      component: expect.objectContaining({ id: 'generated-1' }),
      index: 0
    })
    expect(recordSnapshotCacheMock).toHaveBeenCalledWith('paste')
  })

  it('pastes dashboard components by advancing their grid row and emitting dashboard events', () => {
    dvInfo.value = { type: 'dashboard' }
    const store = copyStore()
    store.copyData = {
      data: [
        {
          id: 'old-dashboard-id',
          component: 'Text',
          canvasId: 'canvas-main',
          style: { top: 0, left: 0, width: 10, height: 10 },
          y: 3,
          sizeY: 4
        }
      ],
      copyCanvasViewInfo: null,
      copyFrom: 'multiplexing'
    } as any

    store.paste()
    vi.runAllTimers()

    expect(addCopyComponentMock).toHaveBeenCalledWith(
      expect.objectContaining({ id: 'generated-1', y: 7 }),
      { 'old-dashboard-id': 'generated-1' },
      null
    )
    expect(adaptCurThemeCommonStyleMock).toHaveBeenCalledWith(
      expect.objectContaining({ id: 'generated-1' })
    )
    expect(emitMock).toHaveBeenCalledWith(
      'addDashboardItem-canvas-main',
      expect.objectContaining({ id: 'generated-1' })
    )
  })

  it('cuts the current component, records a snapshot, and marks the copy as cut', () => {
    curComponent.value = { id: 'cut-me', component: 'Text', style: { top: 10, left: 20 } }
    componentData.value = [{ id: 'cut-me' }]

    const store = copyStore()
    store.cut(componentData.value)

    expect(deleteComponentByIdMock).toHaveBeenCalledWith('cut-me', componentData.value)
    expect(recordSnapshotCacheMock).toHaveBeenCalledWith('cut')
    expect(store.isCut).toBe(true)
    expect(store.copyData?.data).toEqual([
      { id: 'cut-me', component: 'Text', style: { top: 10, left: 20 } }
    ])
  })

  it('restores previously cut data at the original index and updates the active pointer', () => {
    curComponentIndex.value = 3
    const store = copyStore()
    store.isCut = true
    store.copyData = {
      data: [{ id: 'restore-me', component: 'Text' }],
      index: 2
    } as any

    store.restorePreCutData()

    expect(addComponentMock).toHaveBeenCalledWith({
      component: [{ id: 'restore-me', component: 'Text' }],
      index: 2
    })
    expect(curComponentIndex.value).toBe(4)
  })
})
