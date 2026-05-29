import request from '@/config/axios'

export interface RowPermissionRulePayload {
  datasetId: number
  targetType: string
  targetId: number
  filterSql: string
  enabled?: boolean
}

export interface RowPermissionRuleUpdatePayload {
  id: number
  filterSql?: string
  enabled?: boolean
}

export interface ColumnPermissionRulePayload {
  datasetId: number
  fieldId: number
  targetType: string
  targetId: number
  action: string
  enabled?: boolean
}

export interface ColumnPermissionRuleUpdatePayload {
  id: number
  action?: string
  enabled?: boolean
}

export interface PermissionWhitelistPayload {
  userId: number
  datasetId: number
  scope: string
}

export const queryUserApi = data => request.post({ url: '/user/byCurOrg', data })
export const queryUserOptionsApi = () => request.get({ url: '/user/org/option' })
export const queryRoleApi = data => request.post({ url: '/role/byCurOrg', data })

export const resourceTreeApi = (flag: string) => request.get({ url: '/auth/busiResource/' + flag })

export const menuTreeApi = () => request.get({ url: '/auth/menuResource' })

export const resourcePerApi = data => request.post({ url: '/auth/busiPermission', data })

export const menuPerApi = data => request.post({ url: '/auth/menuPermission', data })

export const busiPerSaveApi = data => request.post({ url: '/auth/saveBusiPer', data })
export const menuPerSaveApi = data => request.post({ url: '/auth/saveMenuPer', data })

export const resourceTargetPerApi = data =>
  request.post({ url: '/auth/busiTargetPermission', data })

export const menuTargetPerApi = data => request.post({ url: '/auth/menuTargetPermission', data })

export const busiTargetPerSaveApi = data => request.post({ url: '/auth/saveBusiTargetPer', data })
export const menuTargetPerSaveApi = data => request.post({ url: '/auth/saveMenuTargetPer', data })

export const listRowPermissionApi = (data: { datasetId: number }) =>
  request.post({ url: '/rowPermission/list', data: { dataset_id: data.datasetId } })

export const createRowPermissionApi = (data: RowPermissionRulePayload) =>
  request.post({
    url: '/rowPermission/create',
    data: {
      dataset_id: data.datasetId,
      target_type: data.targetType,
      target_id: data.targetId,
      filter_sql: data.filterSql,
      enabled: data.enabled
    }
  })

export const editRowPermissionApi = (data: RowPermissionRuleUpdatePayload) =>
  request.post({
    url: '/rowPermission/edit',
    data: { id: data.id, filter_sql: data.filterSql, enabled: data.enabled }
  })

export const deleteRowPermissionApi = (ruleId: number) =>
  request.post({ url: `/rowPermission/delete/${ruleId}`, data: {} })

export const listColumnPermissionApi = (data: { datasetId: number }) =>
  request.post({ url: '/columnPermission/list', data: { dataset_id: data.datasetId } })

export const createColumnPermissionApi = (data: ColumnPermissionRulePayload) =>
  request.post({
    url: '/columnPermission/create',
    data: {
      dataset_id: data.datasetId,
      field_id: data.fieldId,
      target_type: data.targetType,
      target_id: data.targetId,
      action: data.action,
      enabled: data.enabled
    }
  })

export const editColumnPermissionApi = (data: ColumnPermissionRuleUpdatePayload) =>
  request.post({
    url: '/columnPermission/edit',
    data: { id: data.id, action: data.action, enabled: data.enabled }
  })

export const deleteColumnPermissionApi = (ruleId: number) =>
  request.post({ url: `/columnPermission/delete/${ruleId}`, data: {} })

export const listPermissionWhitelistApi = () =>
  request.post({ url: '/permissionWhitelist/list', data: {} })

export const createPermissionWhitelistApi = (data: PermissionWhitelistPayload) =>
  request.post({
    url: '/permissionWhitelist/create',
    data: { user_id: data.userId, dataset_id: data.datasetId, scope: data.scope }
  })

export const deletePermissionWhitelistApi = (whitelistId: number) =>
  request.post({ url: `/permissionWhitelist/delete/${whitelistId}`, data: {} })
