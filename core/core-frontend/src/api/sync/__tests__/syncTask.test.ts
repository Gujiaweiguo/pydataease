import { beforeEach, describe, expect, it, vi } from 'vitest'

const { mockRequest } = vi.hoisted(() => ({
  mockRequest: {
    get: vi.fn(),
    post: vi.fn()
  }
}))

vi.mock('@/config/axios', () => ({ default: mockRequest }))

import {
  ITaskInfoRes,
  addApi,
  batchRemoveApi,
  executeOneApi,
  findTaskInfoByIdApi,
  getDatasourceListByTypeApi,
  getDatasourceTableListApi,
  getTaskInfoListApi,
  modifyApi,
  removeApi,
  startTaskApi,
  stopTaskApi
} from '../syncTask'

describe('API: syncTask', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockRequest.get.mockResolvedValue({ data: {} })
    mockRequest.post.mockResolvedValue({ data: {} })
  })

  it('ITaskInfoRes stores constructor arguments on the instance', () => {
    const task = new ITaskInfoRes(
      'task-1',
      'Nightly sync',
      'cron',
      '0 0 * * *',
      'job-key',
      'sync data',
      60,
      3,
      { type: 'mysql', query: '', tables: '', datasourceId: 'ds-1', tableExtract: 'all' },
      {
        type: 'pg',
        fieldList: [],
        tableName: 'orders',
        datasourceId: 'ds-2',
        targetProperty: '{}',
        property: {} as never,
        incrementSync: 'off',
        incrementField: '',
        incrementFieldType: '',
        remarks: '',
        faultToleranceRate: 0,
        incrementOffset: 0,
        incrementOffsetUnit: 'DAY'
      },
      'RUNNING',
      '2026-05-19 00:00:00',
      '2026-05-19 01:00:00',
      { interval: 1, unit: 'DAY' }
    )

    expect(task).toMatchObject({
      id: 'task-1',
      name: 'Nightly sync',
      schedulerType: 'cron',
      schedulerConf: '0 0 * * *',
      taskKey: 'job-key',
      desc: 'sync data',
      executorTimeout: 60,
      executorFailRetryCount: 3,
      status: 'RUNNING',
      startTime: '2026-05-19 00:00:00',
      stopTime: '2026-05-19 01:00:00',
      schedulerOption: { interval: 1, unit: 'DAY' }
    })
  })

  it('getDatasourceListByTypeApi gets the datasource list for a type', async () => {
    await getDatasourceListByTypeApi('MYSQL')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/sync/datasource/list/MYSQL'
    })
  })

  it('getTaskInfoListApi posts task pager filters', async () => {
    const payload = { name: 'nightly' }

    await getTaskInfoListApi(3, 50, payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sync/task/pager/3/50',
      data: payload
    })
  })

  it('executeOneApi gets the execute endpoint for a task id', async () => {
    await executeOneApi('task-2')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/sync/task/execute/task-2'
    })
  })

  it('startTaskApi gets the start endpoint for a task id', async () => {
    await startTaskApi('task-3')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/sync/task/start/task-3'
    })
  })

  it('stopTaskApi gets the stop endpoint for a task id', async () => {
    await stopTaskApi('task-4')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/sync/task/stop/task-4'
    })
  })

  it('addApi posts new task payloads', async () => {
    const payload = { name: 'daily sync' }

    await addApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sync/task/add',
      data: payload
    })
  })

  it('removeApi posts the single task removal endpoint', async () => {
    await removeApi('task-5')

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sync/task/remove/task-5'
    })
  })

  it('batchRemoveApi posts task ids for bulk deletion', async () => {
    const taskIds = ['task-6', 'task-7']

    await batchRemoveApi(taskIds)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sync/task/batch/del',
      data: taskIds
    })
  })

  it('modifyApi posts task update payloads', async () => {
    const payload = { id: 'task-8', name: 'weekly sync' }

    await modifyApi(payload)

    expect(mockRequest.post).toHaveBeenCalledWith({
      url: '/sync/task/update',
      data: payload
    })
  })

  it('findTaskInfoByIdApi gets task details by id', async () => {
    await findTaskInfoByIdApi('task-9')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/sync/task/get/task-9'
    })
  })

  it('getDatasourceTableListApi gets datasource tables by datasource id', async () => {
    await getDatasourceTableListApi('ds-3')

    expect(mockRequest.get).toHaveBeenCalledWith({
      url: '/sync/datasource/table/list/ds-3'
    })
  })
})
