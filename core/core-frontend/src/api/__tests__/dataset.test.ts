import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  mockRequest,
  originNameHandle,
  originNameHandleBack,
  originNameHandleBackWithArr,
  mockCloneDeep,
  nameTrim
} = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn(),
    post: vi.fn()
  },
  originNameHandle: vi.fn(),
  originNameHandleBack: vi.fn(),
  originNameHandleBackWithArr: vi.fn(),
  mockCloneDeep: vi.fn((value: any) => structuredClone(value)),
  nameTrim: vi.fn()
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))
vi.mock('@/utils/CalculateFields', () => ({
  originNameHandle,
  originNameHandleBack,
  originNameHandleBackWithArr
}))
vi.mock('lodash-es', () => ({ cloneDeep: mockCloneDeep }))
vi.mock('@/utils/utils', () => ({ nameTrim }))

import {
  createDatasetTree,
  exportDatasetData,
  getDatasetTree,
  getDatasourceList,
  renameDatasetTree
} from '../dataset'

describe('API: dataset', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('createDatasetTree trims names, normalizes allFields, and posts to create', async () => {
    const payload = {
      name: '  Sales  ',
      nodeType: 'dataset' as const,
      allFields: [{ originName: 'a' }]
    }

    await createDatasetTree(payload)

    expect(nameTrim).toHaveBeenCalledWith(payload)
    expect(mockCloneDeep).toHaveBeenCalledWith(payload)
    expect(originNameHandle).toHaveBeenCalledWith([{ originName: 'a' }])
    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/datasetTree/create',
      data: { name: '  Sales  ', nodeType: 'dataset', allFields: [{ originName: 'a' }] }
    })
  })

  it('renameDatasetTree posts the rename payload after trimming', async () => {
    const payload = { id: 'ds-1', name: '  New Name  ', nodeType: 'dataset' as const }

    await renameDatasetTree(payload)

    expect(nameTrim).toHaveBeenCalledWith(payload)
    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/datasetTree/rename',
      data: payload
    })
  })

  it('getDatasetTree injects the dataset busiFlag before posting', async () => {
    const payload = { keyword: 'orders' }

    await getDatasetTree(payload as any)

    expect(payload).toEqual({ keyword: 'orders', busiFlag: 'dataset' })
    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/datasetTree/tree',
      data: payload
    })
  })

  it('getDatasourceList posts datasource tree filters and optional weight', async () => {
    await getDatasourceList(7)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/datasource/tree',
      data: { busiFlag: 'datasource', weight: 7 }
    })
  })

  it('exportDatasetData posts blob export configuration with loading enabled', async () => {
    const payload = { id: 'ds-2' }

    await exportDatasetData(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/datasetTree/exportDataset',
      method: 'post',
      data: payload,
      loading: true,
      responseType: 'blob'
    })
  })
})
