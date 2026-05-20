import { describe, expect, it, vi, beforeEach } from 'vitest'

const { requestMock } = vi.hoisted(() => ({
  requestMock: {
    get: vi.fn().mockResolvedValue({ data: {} }),
    post: vi.fn().mockResolvedValue({ data: {} })
  }
}))

vi.mock('@/config/axios', () => ({ default: requestMock }))
vi.mock('@/utils/CalculateFields', () => ({
  originNameHandleWithArr: vi.fn()
}))

import {
  findCopyResource,
  updateCheckVersion,
  queryTreeApi,
  queryBusiTreeApi,
  findDvType,
  save,
  checkCanvasChange,
  saveCanvas,
  updatePublishStatus,
  recoverToPublished,
  appCanvasNameCheck,
  updateBase,
  moveResource,
  copyResource,
  deleteLogic,
  querySubjectWithGroupApi,
  saveOrUpdateSubject,
  deleteSubject,
  dvNameCheck,
  storeApi,
  storeStatusApi,
  decompression,
  viewDetailList,
  getComponentInfo,
  export2AppCheck,
  queryOuterParamsDsInfo,
  queryShareBaseApi,
  exportLogApp,
  exportLogTemplate,
  exportLogPDF,
  exportLogImg
} from '../dataVisualization'

describe('dataVisualization API', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('findCopyResource calls request.get with correct url', async () => {
    await findCopyResource('dv123', 'dashboard')
    expect(requestMock.get).toHaveBeenCalledWith({
      url: '/dataVisualization/findCopyResource/dv123/dashboard'
    })
  })

  it('updateCheckVersion calls request.get with correct url', async () => {
    await updateCheckVersion('dv456')
    expect(requestMock.get).toHaveBeenCalledWith({
      url: '/dataVisualization/updateCheckVersion/dv456'
    })
  })

  it('queryTreeApi calls request.post with correct url and data', async () => {
    const data = { busiFlag: 'dashboard' }
    await queryTreeApi(data as any)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/dataVisualization/tree',
      data
    })
  })

  it('queryBusiTreeApi calls request.post with correct url and data', async () => {
    const data = { busiFlag: 'dataV' }
    await queryBusiTreeApi(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/dataVisualization/interactiveTree',
      data
    })
  })

  it('findDvType calls request.get with correct url', async () => {
    await findDvType('dv789')
    expect(requestMock.get).toHaveBeenCalledWith({
      url: '/dataVisualization/findDvType/dv789'
    })
  })

  it('save calls request.post with correct url and data', async () => {
    const data = { name: 'test' }
    await save(data)
    expect(requestMock.post).toHaveBeenCalledWith({ url: '/dataVisualization/save', data })
  })

  it('checkCanvasChange calls request.post with loading flag', async () => {
    const data = { id: 'dv1' }
    await checkCanvasChange(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/dataVisualization/checkCanvasChange',
      data,
      loading: true
    })
  })

  it('saveCanvas calls request.post with loading flag', async () => {
    const data = { id: 'dv1' }
    await saveCanvas(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/dataVisualization/saveCanvas',
      data,
      loading: true
    })
  })

  it('updatePublishStatus calls request.post with loading false', async () => {
    const data = { id: 'dv1', status: 1 }
    await updatePublishStatus(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/dataVisualization/updatePublishStatus',
      data,
      loading: false
    })
  })

  it('recoverToPublished calls request.post with loading true', async () => {
    const data = { id: 'dv1' }
    await recoverToPublished(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/dataVisualization/recoverToPublished',
      data,
      loading: true
    })
  })

  it('appCanvasNameCheck calls request.post', async () => {
    const data = { name: 'canvas1' }
    await appCanvasNameCheck(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/dataVisualization/appCanvasNameCheck',
      data,
      loading: false
    })
  })

  it('updateBase calls request.post with correct url and data', async () => {
    const data = { id: 'dv1', name: 'updated' }
    await updateBase(data)
    expect(requestMock.post).toHaveBeenCalledWith({ url: '/dataVisualization/updateBase', data })
  })

  it('moveResource calls request.post with correct url and data', async () => {
    const data = { id: 'dv1', pid: 'p1' }
    await moveResource(data)
    expect(requestMock.post).toHaveBeenCalledWith({ url: '/dataVisualization/move', data })
  })

  it('copyResource calls request.post with correct url and data', async () => {
    const data = { id: 'dv1' }
    await copyResource(data)
    expect(requestMock.post).toHaveBeenCalledWith({ url: '/dataVisualization/copy', data })
  })

  it('deleteLogic calls request.post with correct url', async () => {
    await deleteLogic('dv1', 'dashboard')
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/dataVisualization/deleteLogic/dv1/dashboard'
    })
  })

  it('querySubjectWithGroupApi calls request.post', async () => {
    const data = { id: 1 }
    await querySubjectWithGroupApi(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/visualizationSubject/querySubjectWithGroup',
      data
    })
  })

  it('saveOrUpdateSubject calls request.post', async () => {
    const data = { id: 1, name: 'theme1' }
    await saveOrUpdateSubject(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/visualizationSubject/update',
      data
    })
  })

  it('deleteSubject calls request.post with correct url', async () => {
    await deleteSubject(42)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/visualizationSubject/delete/42'
    })
  })

  it('dvNameCheck calls request.post', async () => {
    const data = { name: 'test', pid: 1 }
    await dvNameCheck(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/dataVisualization/nameCheck',
      data
    })
  })

  it('storeApi calls request.post', async () => {
    const data = { id: 'dv1' }
    await storeApi(data)
    expect(requestMock.post).toHaveBeenCalledWith({ url: '/store/execute', data })
  })

  it('storeStatusApi calls request.get with correct url', async () => {
    await storeStatusApi('dv1')
    expect(requestMock.get).toHaveBeenCalledWith({ url: '/store/favorited/dv1' })
  })

  it('decompression calls request.post with loading flag', async () => {
    const data = { file: 'data.zip' }
    await decompression(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/dataVisualization/decompression',
      data,
      loading: true
    })
  })

  it('viewDetailList calls request.get with correct url', async () => {
    await viewDetailList('dv1')
    expect(requestMock.get).toHaveBeenCalledWith({
      url: '/dataVisualization/viewDetailList/dv1',
      method: 'get',
      loading: false
    })
  })

  it('getComponentInfo calls request.get with correct url', async () => {
    await getComponentInfo('dv1')
    expect(requestMock.get).toHaveBeenCalledWith({
      url: '/panel/view/getComponentInfo/dv1',
      loading: false
    })
  })

  it('export2AppCheck calls request.post with loading flag', async () => {
    const data = { dvId: 'dv1' }
    await export2AppCheck(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/dataVisualization/export2AppCheck',
      data,
      loading: true
    })
  })

  it('queryOuterParamsDsInfo calls request.get', async () => {
    await queryOuterParamsDsInfo('dv1')
    expect(requestMock.get).toHaveBeenCalledWith({
      url: '/outerParams/queryDsWithVisualizationId/dv1',
      method: 'get',
      loading: false
    })
  })

  it('queryShareBaseApi calls request.get', async () => {
    await queryShareBaseApi()
    expect(requestMock.get).toHaveBeenCalledWith({
      url: '/sysParameter/shareBase',
      loading: false
    })
  })

  it('exportLogApp calls request.post', async () => {
    const data = { id: 1 }
    await exportLogApp(data)
    expect(requestMock.post).toHaveBeenCalledWith({ url: '/dataVisualization/exportLogApp', data })
  })

  it('exportLogTemplate calls request.post', async () => {
    const data = { id: 1 }
    await exportLogTemplate(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/dataVisualization/exportLogTemplate',
      data
    })
  })

  it('exportLogPDF calls request.post', async () => {
    const data = { id: 1 }
    await exportLogPDF(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/dataVisualization/exportLogPDF',
      data
    })
  })

  it('exportLogImg calls request.post', async () => {
    const data = { id: 1 }
    await exportLogImg(data)
    expect(requestMock.post).toHaveBeenCalledWith({
      url: '/dataVisualization/exportLogImg',
      data
    })
  })
})
