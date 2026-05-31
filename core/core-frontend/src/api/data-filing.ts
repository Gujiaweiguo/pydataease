import request from '@/config/axios'

export type FilingConfigStatus = 'draft' | 'published' | 'disabled'
export type SubmissionStatus = 'pending' | 'success' | 'failed' | 'retrying'
export type AuditAction = 'submit' | 'publish' | 'disable' | 'retry' | 'config_update'
export type AuditOutcome = 'success' | 'failure'

export interface FilingConfig {
  id: number
  name: string
  status: FilingConfigStatus
  targetDatasourceId: number | null
  targetTable: string | null
  formSchema: Record<string, any>
  fieldMapping: Record<string, any>
  idempotencyWindowSeconds: number
  oid: number | null
  creatorUid: number | null
  createTime: string | null
  updateTime: string | null
}

export interface FilingConfigCreateRequest {
  name: string
  targetDatasourceId?: number | null
  targetTable?: string | null
  formSchema: Record<string, any>
  fieldMapping: Record<string, any>
  idempotencyWindowSeconds?: number
  oid?: number | null
}

export interface FilingConfigUpdateRequest {
  name?: string | null
  targetDatasourceId?: number | null
  targetTable?: string | null
  formSchema?: Record<string, any> | null
  fieldMapping?: Record<string, any> | null
  idempotencyWindowSeconds?: number | null
}

export interface FilingSubmission {
  id: number
  filingId: number
  payloadHash: string | null
  payload: Record<string, any> | null
  status: SubmissionStatus
  errorMessage: string | null
  submitterUid: number | null
  retryCount: number
  createTime: string | null
  updateTime: string | null
}

export interface FilingAudit {
  id: number
  filingId: number
  submissionId: number | null
  action: AuditAction
  actorUid: number | null
  details: Record<string, any> | null
  outcome: AuditOutcome
  errorCode: string | null
  createTime: string | null
}

// Config CRUD
export const filingConfigList = (status?: string) =>
  request.get({ url: '/data-filing/config/list', params: { status } })

export const filingConfigGet = (id: number) => request.get({ url: `/data-filing/config/${id}` })

export const filingConfigCreate = (data: FilingConfigCreateRequest) =>
  request.post({ url: '/data-filing/config/create', data })

export const filingConfigUpdate = (id: number, data: FilingConfigUpdateRequest) =>
  request.put({ url: `/data-filing/config/${id}`, data })

export const filingConfigPublish = (id: number) =>
  request.post({ url: `/data-filing/config/${id}/publish` })

export const filingConfigDisable = (id: number) =>
  request.post({ url: `/data-filing/config/${id}/disable` })

export const filingConfigDelete = (id: number) =>
  request.delete({ url: `/data-filing/config/${id}` })

// Submissions
export const filingSubmit = (filingId: number, data: Record<string, any>) =>
  request.post({ url: `/data-filing/${filingId}/submit`, data })

export const filingSubmissions = (filingId: number) =>
  request.get({ url: `/data-filing/${filingId}/submissions` })

export const filingSubmissionGet = (submissionId: number) =>
  request.get({ url: `/data-filing/submission/${submissionId}` })

export const filingSubmissionRetry = (submissionId: number) =>
  request.post({ url: `/data-filing/submission/${submissionId}/retry` })

// Audit
export const filingAuditList = (filingId: number) =>
  request.get({ url: `/data-filing/${filingId}/audit` })
