import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'

const {
  addComponentMock,
  checkJoinGroupMock,
  componentData,
  createGroupStyleMock,
  curComponent,
  curOriginThemes,
  decomposeComponentMock,
  dollarMock,
  emitMock,
  generateIDMock,
  setCurComponentMock
} = vi.hoisted(() => ({
  addComponentMock: vi.fn(),
  checkJoinGroupMock: vi.fn(),
  componentData: { value: [] as any[] },
  createGroupStyleMock: vi.fn(),
  curComponent: { value: null as any },
  curOriginThemes: { value: 'light' },
  decomposeComponentMock: vi.fn(),
  dollarMock: vi.fn(),
  emitMock: vi.fn(),
  generateIDMock: vi.fn(),
  setCurComponentMock: vi.fn()
}))

vi.mock('pinia', async () => {
  const actual = await vi.importActual<typeof import('pinia')>('pinia')
  return {
    ...actual,
    storeToRefs: () => ({
      curComponent,
      componentData,
      curOriginThemes
    })
  }
})

vi.mock('../dvMain', () => ({
  dvMainStoreWithOut: () => ({
    curComponent,
    componentData,
    curOriginThemes,
    addComponent: addComponentMock,
    setCurComponent: setCurComponentMock,
    deleteComponentById: vi.fn()
  })
}))

vi.mock('@/utils/utils', () => ({
  $: dollarMock,
  deepCopy: <T>(value: T) => JSON.parse(JSON.stringify(value))
}))

vi.mock('@/utils/decomposeComponent', () => ({ default: decomposeComponentMock }))
vi.mock('@/utils/generateID', () => ({ generateID: generateIDMock }))

vi.mock('@/custom-component/component-list', () => ({
  commonStyle: { rotate: 0, left: 0, top: 0, width: 0, height: 0 },
  commonAttr: { attrKey: 'base-attr' },
  COMMON_COMPONENT_BACKGROUND_MAP: {
    light: { backgroundColor: '#ffffff' },
    dark: { backgroundColor: '#000000' }
  }
}))

vi.mock('@/utils/style', () => ({
  createGroupStyle: createGroupStyleMock,
  getComponentRotatedStyle: (style: any) => ({
    ...style,
    right: style.left + style.width,
    bottom: style.top + style.height
  })
}))

vi.mock('@/utils/eventBus', () => ({ default: { emit: emitMock } }))

vi.mock('@/utils/canvasUtils', () => ({
  canvasIdMapCheck: vi.fn(),
  checkJoinGroup: checkJoinGroupMock,
  isTabCanvas: vi.fn(() => false)
}))

vi.mock('@/hooks/web/useI18n', () => ({
  useI18n: () => ({ t: (key: string) => key })
}))

import { composeStore } from '../compose'

describe('composeStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
    componentData.value = []
    curComponent.value = null
    curOriginThemes.value = 'light'
    generateIDMock.mockReturnValue('group-1')
    dollarMock.mockReturnValue({ getBoundingClientRect: () => ({ left: 0, top: 0 }) })
    addComponentMock.mockImplementation(({ component }: { component: any }) => {
      componentData.value.push(component)
    })
  })

  it('stores editor references and key modifier flags', () => {
    const store = composeStore()

    store.getEditor('canvas-main')
    store.setLaterIndex(3)
    store.setSpaceDownStatus(true)
    store.setIsCtrlOrCmdDownStatus(true)
    store.setIsShiftDownStatus(true)

    expect(store.editorMap['canvas-main']).toEqual({ getBoundingClientRect: expect.any(Function) })
    expect(store.laterIndex).toBe(3)
    expect(store.isSpaceDown).toBe(true)
    expect(store.isCtrlOrCmdDown).toBe(true)
    expect(store.isShiftDown).toBe(true)
  })

  it('clears single-component alignment selections without attempting a group action', () => {
    const store = composeStore()
    store.areaData.components = [{ id: 'single', style: { left: 0, top: 0, width: 10, height: 10 } }]

    store.alignment('left')

    expect(store.areaData.components).toEqual([])
  })

  it('calculates bounding boxes for selected components', () => {
    const store = composeStore()
    store.areaData = {
      style: { left: 0, top: 0, width: 0, height: 0 },
      components: [
        { style: { left: 30, top: 10, width: 40, height: 20 } },
        { style: { left: 5, top: 25, width: 20, height: 35 } }
      ] as any
    }

    store.calcComposeArea()

    expect(store.areaData.style).toEqual({ left: 5, top: 10, width: 65, height: 50 })
  })

  it('removes only non-GroupArea components during batch delete', () => {
    const store = composeStore()
    componentData.value = [{ id: 'delete-1' }, { id: 'keep-area', component: 'GroupArea' }, { id: 'delete-2' }]

    store.batchDeleteComponent([
      { id: 'delete-1', component: 'Text' },
      { id: 'keep-area', component: 'GroupArea' },
      { id: 'delete-2', component: 'Picture' }
    ])

    expect(componentData.value).toEqual([{ id: 'keep-area', component: 'GroupArea' }])
  })

  it('creates a new group from joinable components and existing groups', () => {
    const existingChild = {
      id: 'group-child',
      component: 'Text',
      canvasId: 'Group-old',
      style: { left: 15, top: 15, width: 20, height: 20 }
    }
    const existingGroup = {
      id: 'existing-group',
      component: 'Group',
      canvasId: 'canvas-main',
      style: { left: 0, top: 0, width: 100, height: 100 },
      propValue: [existingChild]
    }
    const plainComponent = {
      id: 'plain-1',
      component: 'Text',
      canvasId: 'canvas-main',
      style: { left: 40, top: 50, width: 30, height: 30 }
    }
    const groupArea = {
      id: 'group-area',
      component: 'GroupArea',
      canvasId: 'canvas-main',
      style: { left: 0, top: 0, width: 0, height: 0 }
    }

    componentData.value = [existingGroup, plainComponent, groupArea]
    checkJoinGroupMock.mockImplementation(component => component.component === 'Text')

    const store = composeStore()
    store.getEditor('canvas-main')
    store.areaData = {
      style: { left: 0, top: 0, width: 0, height: 0 },
      components: [existingGroup, groupArea, plainComponent] as any
    }

    store.compose('canvas-main')

    expect(decomposeComponentMock).toHaveBeenCalledWith(existingChild, { left: 0, top: 0 }, existingGroup.style)
    expect(addComponentMock).toHaveBeenCalledTimes(1)
    expect(componentData.value).toHaveLength(2)
    expect(componentData.value[1]).toEqual(
      expect.objectContaining({
        id: 'group-1',
        component: 'Group',
        name: 'visualization.view_group',
        label: 'visualization.view_group',
        canvasActive: false,
        attrKey: 'base-attr',
        propValue: [
          expect.objectContaining({ id: 'group-child', canvasId: 'Group-group-1' }),
          expect.objectContaining({ id: 'plain-1', canvasId: 'Group-group-1' })
        ]
      })
    )
    expect(createGroupStyleMock).toHaveBeenCalledWith(componentData.value[1])
    expect(setCurComponentMock).toHaveBeenCalledWith({ component: componentData.value[1], index: 1 })
    expect(emitMock).toHaveBeenCalledWith('hideArea-canvas-main')
    expect(store.areaData.components).toEqual([])
  })
})
