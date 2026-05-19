import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  canvasStyleDataRef,
  componentDataRef,
  canvasViewDataInfoRef,
  canvasViewInfoRef,
  dvInfoRef,
  embeddedStore,
  findResourceAsBase64Mock
} = vi.hoisted(() => ({
  canvasStyleDataRef: { value: { background: '' } },
  componentDataRef: { value: [] as any[] },
  canvasViewDataInfoRef: { value: {} },
  canvasViewInfoRef: { value: {} },
  dvInfoRef: { value: { type: 'dashboard' } },
  embeddedStore: { baseUrl: '' },
  findResourceAsBase64Mock: vi.fn()
}))

vi.mock('pinia', async () => {
  const actual = await vi.importActual<typeof import('pinia')>('pinia')
  return {
    ...actual,
    storeToRefs: () => ({
      canvasStyleData: canvasStyleDataRef,
      componentData: componentDataRef,
      canvasViewInfo: canvasViewInfoRef,
      canvasViewDataInfo: canvasViewDataInfoRef,
      dvInfo: dvInfoRef
    })
  }
})

vi.mock('@/store/modules/data-visualization/dvMain', () => ({
  dvMainStoreWithOut: () => ({})
}))

vi.mock('@/store/modules/embedded', () => ({
  useEmbedded: () => embeddedStore
}))

vi.mock('@/api/staticResource', () => ({
  findResourceAsBase64: findResourceAsBase64Mock
}))

vi.mock('html2canvas', () => ({ default: vi.fn() }))
vi.mock('jspdf', () => ({ default: vi.fn() }))
vi.mock('file-saver', () => ({ default: { saveAs: vi.fn() } }))
vi.mock('modern-screenshot', () => ({ domToPng: vi.fn() }))
vi.mock('@/utils/canvasUtils', () => ({ initCanvasDataPrepare: vi.fn() }))
vi.mock('@/utils/utils', () => ({ deepCopy: <T>(value: T) => JSON.parse(JSON.stringify(value)) }))

const loadModule = async () => import('../imgUtils')

describe('imgUtils', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.resetModules()
    vi.stubEnv('VITE_API_BASEPATH', '/api/')
    embeddedStore.baseUrl = ''
    canvasStyleDataRef.value = { background: '' }
    componentDataRef.value = []
    dvInfoRef.value = { type: 'dashboard' }
  })

  it('normalizes duplicated de2api path separators', async () => {
    const { formatterUrl } = await loadModule()

    expect(formatterUrl('https://demo.com//de2api/chart')).toBe('https://demo.com/de2api/chart')
  })

  it('transforms static-resource urls with base paths and embedded origins', async () => {
    const { imgUrlTrans } = await loadModule()

    embeddedStore.baseUrl = 'https://embed.example.com'

    expect(imgUrlTrans('/static-resource/logo.png')).toBe(
      'https://embed.example.comstatic-resource/logo.png'
    )
  })

  it('returns non-string values unchanged and normalizes ordinary urls', async () => {
    const { imgUrlTrans } = await loadModule()

    expect(imgUrlTrans({ url: 'raw' })).toEqual({ url: 'raw' })
    expect(imgUrlTrans('https://demo.com//de2api/image.png')).toBe('https://demo.com/de2api/image.png')
  })

  it('converts data urls into typed blobs', async () => {
    const { dataURLToBlob } = await loadModule()

    const blob = dataURLToBlob('data:text/plain;base64,SGk=')

    expect(blob.type).toBe('text/plain')
    expect(blob.size).toBe(2)
    await expect(blob.text()).resolves.toBe('Hi')
  })

  it('collects nested static resources and forwards the base64 response', async () => {
    const { findStaticSource } = await loadModule()
    canvasStyleDataRef.value = { background: '/static-resource/canvas.png' }
    componentDataRef.value = [
      {
        component: 'Picture',
        commonBackground: { outerImage: '' },
        propValue: { url: '/static-resource/picture.png' }
      },
      {
        component: 'UserView',
        innerType: 'picture-group',
        commonBackground: { outerImage: '' },
        propValue: { urlList: [{ url: '/static-resource/gallery.png' }, { url: '/external.png' }] }
      },
      {
        component: 'Group',
        commonBackground: { outerImage: '/static-resource/group-bg.png' },
        propValue: [
          {
            component: 'Picture',
            commonBackground: { outerImage: '' },
            propValue: { url: '/static-resource/group-picture.png' }
          }
        ]
      },
      {
        component: 'DeTabs',
        commonBackground: { outerImage: '' },
        propValue: [
          {
            componentData: [
              {
                component: 'Picture',
                commonBackground: { outerImage: '' },
                propValue: { url: '/static-resource/tab-picture.png' }
              }
            ]
          }
        ]
      }
    ]
    findResourceAsBase64Mock.mockResolvedValue({ data: { ok: true } })

    const result = await new Promise(resolve => {
      findStaticSource(resolve)
    })

    expect(findResourceAsBase64Mock).toHaveBeenCalledWith({
      resourcePathList: [
        '/static-resource/canvas.png',
        '/static-resource/picture.png',
        '/static-resource/gallery.png',
        '/static-resource/group-bg.png',
        '/static-resource/group-picture.png',
        '/static-resource/tab-picture.png'
      ]
    })
    expect(result).toEqual({ ok: true })
  })

  it('invokes the callback asynchronously without hitting the api when nothing is static', async () => {
    vi.useFakeTimers()
    const { findStaticSource } = await loadModule()
    canvasStyleDataRef.value = { background: '/plain/background.png' }
    componentDataRef.value = [
      { component: 'Text', commonBackground: { outerImage: '' }, propValue: {} }
    ]

    const callback = vi.fn()
    findStaticSource(callback)
    vi.runAllTimers()

    expect(findResourceAsBase64Mock).not.toHaveBeenCalled()
    expect(callback).toHaveBeenCalledWith()
    vi.useRealTimers()
  })
})
