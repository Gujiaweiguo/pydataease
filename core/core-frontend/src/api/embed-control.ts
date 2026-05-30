import request from '@/config/axios'

export type EmbedResourceType = 'dashboard' | 'chart' | 'datav' | 'dataFiling'

export interface EmbedConfig {
  id: number
  resourceType: EmbedResourceType
  embedEnabled: boolean
  allowedDomains: string[]
  passwordRequired: boolean
  ticketRequired: boolean
  maxExpiryHours: number | null
  extraConfig: Record<string, any> | null
  createTime: string | null
  updateTime: string | null
}

export interface EmbedConfigUpdateRequest {
  embedEnabled?: boolean | null
  allowedDomains?: string[] | null
  passwordRequired?: boolean | null
  ticketRequired?: boolean | null
  maxExpiryHours?: number | null
  extraConfig?: Record<string, any> | null
}

export interface EmbedCheckResult {
  allowed: boolean
  resourceType: string
}

export const embedControlList = () => request.get({ url: '/embed-control/list' })

export const embedControlGet = (resourceType: string) =>
  request.get({ url: `/embed-control/${resourceType}` })

export const embedControlUpdate = (resourceType: string, data: EmbedConfigUpdateRequest) =>
  request.put({ url: `/embed-control/${resourceType}`, data })

export const embedControlCheck = (resourceType: string, domain?: string) =>
  request.get({ url: `/embed-control/${resourceType}/check`, params: { domain } })
