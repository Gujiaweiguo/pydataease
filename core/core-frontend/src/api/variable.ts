import request from '@/config/axios'

export interface VariablePayload {
  id?: number
  name?: string
  alias?: string
  type?: string
  remark?: string
}

export interface VariableQueryPayload {
  keyword?: string
}

export interface VariableValueQueryPayload {
  variableId?: number
  keyword?: string
}

export interface VariableValuePayload {
  id?: number
  variableId?: number
  value?: string
  name?: string
  remark?: string
  userId?: number
}

export interface VariableValueBatchDeletePayload {
  ids: number[]
}

export const variableCreateApi = (data: VariablePayload) =>
  request.post({ url: '/sysVariable/create', data })

export const variableEditApi = (data: VariablePayload) =>
  request.post({ url: '/sysVariable/edit', data })

export const variableDetailApi = (id: number) => request.get({ url: '/sysVariable/detail/' + id })

export const variableDeletelApi = (id: number) => request.get({ url: '/sysVariable/delete/' + id })

export const searchVariableApi = async (data: VariableQueryPayload) =>
  request.post({ url: '/sysVariable/query', data })

export const valueSelectedForVariableApi = (
  page: number,
  limit: number,
  data: VariableValueQueryPayload
) => request.post({ url: `/sysVariable/value/selected/${page}/${limit}`, data })

export const valueForVariable = (id: number) =>
  request.get({ url: '/sysVariable/value/selected/' + id })

export const variableValueCreateApi = (data: VariableValuePayload) =>
  request.post({ url: '/sysVariable/value/create', data })

export const variableValueDeletelApi = (id: number) =>
  request.get({ url: '/sysVariable/value/delete/' + id })

export const variableValueEditApi = (data: VariableValuePayload) =>
  request.post({ url: '/sysVariable/value/edit', data })

export const batchDelApi = (data: VariableValueBatchDeletePayload) =>
  request.post({ url: '/sysVariable/value/batchDel', data })
