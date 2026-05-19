import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest, originNameHandleWithArr, originNameHandleBackWithArr, mockCloneDeep } = vi.hoisted(
  () => ({
    mockRequest: {
      get: vi.fn(),
      post: vi.fn()
    },
    originNameHandleWithArr: vi.fn(),
    originNameHandleBackWithArr: vi.fn(),
    mockCloneDeep: vi.fn((value: any) => structuredClone(value))
  })
)

vi.mock('@/config/axios', () => ({ default: mockRequest }))
vi.mock('@/utils/CalculateFields', () => ({
  originNameHandleWithArr,
  originNameHandleBackWithArr
}))
vi.mock('lodash-es', () => ({ cloneDeep: mockCloneDeep }))

import {
  checkSameDataSet,
  getChart,
  getData,
  innerExportDetails,
  saveChart
} from '../chart'

describe('API: chart', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ code: 0, data: {} })
  })

  it('getChart posts an empty body to the chart lookup endpoint', async () => {
    await getChart('chart-1')

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/chart/getChart/chart-1',
      data: {}
    })
  })

  it('saveChart removes nested data before posting the chart payload', async () => {
    const payload = { id: 'chart-2', name: 'Revenue', data: { stale: true } }

    await saveChart(payload)

    expect(payload).toEqual({ id: 'chart-2', name: 'Revenue' })
    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/chart/save',
      data: { id: 'chart-2', name: 'Revenue' }
    })
  })

  it('getData clones the payload, strips nested data, and posts to chartData', async () => {
    const payload = {
      id: 'chart-3',
      data: { remove: true },
      xAxis: [{ originName: 'sales' }],
      extColor: []
    }

    await getData(payload)

    expect(payload).toEqual({
      id: 'chart-3',
      xAxis: [{ originName: 'sales' }],
      extColor: []
    })
    expect(mockCloneDeep).toHaveBeenCalledWith(payload)
    expect(originNameHandleWithArr).toHaveBeenCalledWith(expect.any(Object), [
      'xAxis',
      'xAxisExt',
      'yAxis',
      'yAxisExt',
      'extBubble',
      'extLabel',
      'extStack',
      'extTooltip',
      'extColor'
    ])
    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/chartData/getData',
      data: {
        id: 'chart-3',
        xAxis: [{ originName: 'sales' }],
        extColor: []
      }
    })
  })

  it('innerExportDetails posts blob export options with loading enabled', async () => {
    const payload = { chartId: 'chart-4' }

    await innerExportDetails(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/chartData/innerExportDetails',
      method: 'post',
      data: payload,
      loading: true,
      responseType: 'blob'
    })
  })

  it('checkSameDataSet requests the compare endpoint with GET', async () => {
    await checkSameDataSet('source-id', 'target-id')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/chart/checkSameDataSet/source-id/target-id'
    })
  })
})
