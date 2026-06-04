import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))

import * as dataVisualizationApi from '../visualization/dataVisualization'

describe('API: dataVisualization', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('findCopyResource gets the copy resource path with dv id and business flag', async () => {
    await dataVisualizationApi.findCopyResource('dv-1', 'panel')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/dataVisualization/findCopyResource/dv-1/panel'
    })
  })

  it('findById posts provided business flags and default attach info', async () => {
    await dataVisualizationApi.findById('dv-2', 'dashboard')

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/findById',
      data: { id: 'dv-2', busiFlag: 'dashboard', source: 'main', taskId: null }
    })
  })

  it('findById resolves a missing business flag via findDvType before posting', async () => {
    mockRequest.get.mockResolvedValueOnce({ data: 'template' })

    await dataVisualizationApi.findById('dv-3', '', { source: 'share', taskId: 'task-1' })

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/dataVisualization/findDvType/dv-3'
    })
    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/findById',
      data: { id: 'dv-3', busiFlag: 'template', source: 'share', taskId: 'task-1' }
    })
  })

  it('updateCheckVersion gets the version check endpoint', async () => {
    await dataVisualizationApi.updateCheckVersion('dv-4')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/dataVisualization/updateCheckVersion/dv-4'
    })
  })

  it('queryTreeApi posts the tree payload and unwraps response data', async () => {
    const response = { data: [{ id: 'folder-1' }] }
    const payload = { busiFlag: 'dashboard' }
    mockRequest.post.mockResolvedValueOnce(response)

    const result = await dataVisualizationApi.queryTreeApi(payload as any)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/tree',
      data: payload
    })
    expect(result).toEqual(response.data)
  })

  it('queryBusiTreeApi posts the interactive tree payload and unwraps response data', async () => {
    const response = { data: [{ id: 'leaf-1' }] }
    const payload = { keyword: 'sales' }
    mockRequest.post.mockResolvedValueOnce(response)

    const result = await dataVisualizationApi.queryBusiTreeApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/interactiveTree',
      data: payload
    })
    expect(result).toEqual(response.data)
  })

  it('findDvType gets the visualization type by id', async () => {
    await dataVisualizationApi.findDvType('dv-5')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/dataVisualization/findDvType/dv-5'
    })
  })

  it('save posts the visualization payload', async () => {
    const payload = { name: 'Overview' }

    await dataVisualizationApi.save(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/save',
      data: payload
    })
  })

  it('checkCanvasChange posts with loading enabled', async () => {
    const payload = { canvasId: 'canvas-1' }

    await dataVisualizationApi.checkCanvasChange(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/checkCanvasChange',
      data: payload,
      loading: true
    })
  })

  it('saveCanvas posts with loading enabled', async () => {
    const payload = { canvasId: 'canvas-2' }

    await dataVisualizationApi.saveCanvas(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/saveCanvas',
      data: payload,
      loading: true
    })
  })

  it('updatePublishStatus posts with loading disabled', async () => {
    const payload = { id: 'dv-6', publish: true }

    await dataVisualizationApi.updatePublishStatus(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/updatePublishStatus',
      data: payload,
      loading: false
    })
  })

  it('recoverToPublished posts with loading enabled', async () => {
    const payload = { id: 'dv-7' }

    await dataVisualizationApi.recoverToPublished(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/recoverToPublished',
      data: payload,
      loading: true
    })
  })

  it('appCanvasNameCheck posts with loading disabled', async () => {
    const payload = { name: 'Mobile Canvas' }

    await dataVisualizationApi.appCanvasNameCheck(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/appCanvasNameCheck',
      data: payload,
      loading: false
    })
  })

  it('updateBase posts the base metadata payload', async () => {
    const payload = { id: 'dv-8', name: 'Executive' }

    await dataVisualizationApi.updateBase(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/updateBase',
      data: payload
    })
  })

  it('updateCanvas posts canvas data with loading enabled', async () => {
    const payload = {
      canvasViewInfo: {
        viewA: {
          xAxis: [{ originName: 'sales' }],
          extColor: []
        },
        viewB: {
          yAxis: [{ originName: 'profit' }]
        }
      }
    }

    await dataVisualizationApi.updateCanvas(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/updateCanvas',
      data: payload,
      loading: true
    })
  })

  it('moveResource posts the move payload', async () => {
    const payload = { sourceId: 'dv-9', targetPid: 'folder-2' }

    await dataVisualizationApi.moveResource(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/move',
      data: payload
    })
  })

  it('copyResource posts the copy payload', async () => {
    const payload = { sourceId: 'dv-10', name: 'Copy' }

    await dataVisualizationApi.copyResource(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/copy',
      data: payload
    })
  })

  it('deleteLogic posts the delete path with dv id and business flag', async () => {
    await dataVisualizationApi.deleteLogic('dv-11', 'panel')

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/deleteLogic/dv-11/panel'
    })
  })

  it('querySubjectWithGroupApi posts the subject query payload', async () => {
    const payload = { keyword: 'marketing' }

    await dataVisualizationApi.querySubjectWithGroupApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/visualizationSubject/querySubjectWithGroup',
      data: payload
    })
  })

  it('saveOrUpdateSubject posts the subject payload', async () => {
    const payload = { id: 'subject-1', name: 'North America' }

    await dataVisualizationApi.saveOrUpdateSubject(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/visualizationSubject/update',
      data: payload
    })
  })

  it('deleteSubject posts the subject id in the endpoint path', async () => {
    await dataVisualizationApi.deleteSubject('subject-2')

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/visualizationSubject/delete/subject-2'
    })
  })

  it('dvNameCheck posts the visualization name payload', async () => {
    const payload = { name: 'Quarterly Summary' }

    await dataVisualizationApi.dvNameCheck(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/nameCheck',
      data: payload
    })
  })

  it('storeApi posts store execution payloads', async () => {
    const payload = { resourceId: 'dv-12' }

    await dataVisualizationApi.storeApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/store/execute',
      data: payload
    })
  })

  it('storeStatusApi gets favorite status by id', async () => {
    await dataVisualizationApi.storeStatusApi('dv-13')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/store/favorited/dv-13'
    })
  })

  it('decompression posts with loading enabled', async () => {
    const payload = { compressed: 'zip-data' }

    await dataVisualizationApi.decompression(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/decompression',
      data: payload,
      loading: true
    })
  })

  it('viewDetailList gets detail list with loading disabled', async () => {
    await dataVisualizationApi.viewDetailList('dv-14')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/dataVisualization/viewDetailList/dv-14',
      method: 'get',
      loading: false
    })
  })

  it('getComponentInfo gets panel component info with loading disabled', async () => {
    await dataVisualizationApi.getComponentInfo('dv-15')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/panel/view/getComponentInfo/dv-15',
      loading: false
    })
  })

  it('export2AppCheck posts export checks with loading enabled', async () => {
    const payload = { id: 'dv-16' }

    await dataVisualizationApi.export2AppCheck(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/export2AppCheck',
      data: payload,
      loading: true
    })
  })

  it('queryOuterParamsDsInfo gets outer param datasource info with loading disabled', async () => {
    await dataVisualizationApi.queryOuterParamsDsInfo('dv-17')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/outerParams/queryDsWithVisualizationId/dv-17',
      method: 'get',
      loading: false
    })
  })

  it('queryShareBaseApi gets share base settings with loading disabled', async () => {
    await dataVisualizationApi.queryShareBaseApi()

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/sysParameter/shareBase',
      loading: false
    })
  })

  it('exportLogApp posts application export log payloads', async () => {
    const payload = { id: 'log-1' }

    await dataVisualizationApi.exportLogApp(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/exportLogApp',
      data: payload
    })
  })

  it('exportLogTemplate posts template export log payloads', async () => {
    const payload = { id: 'log-2' }

    await dataVisualizationApi.exportLogTemplate(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/exportLogTemplate',
      data: payload
    })
  })

  it('exportLogPDF posts pdf export log payloads', async () => {
    const payload = { id: 'log-3' }

    await dataVisualizationApi.exportLogPDF(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/exportLogPDF',
      data: payload
    })
  })

  it('exportLogImg posts image export log payloads', async () => {
    const payload = { id: 'log-4' }

    await dataVisualizationApi.exportLogImg(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/dataVisualization/exportLogImg',
      data: payload
    })
  })
})
