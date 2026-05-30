import request from '@/config/axios'

export interface FeatureToggleRequest {
  key: string
  enabled: boolean
}

export interface AuthStatusItem {
  type: string
  name: string
  enabled: boolean
  isDefault: boolean
}

export const featureToggle = (data: FeatureToggleRequest) =>
  request.post({ url: '/sysParameter/feature/toggle', data })

export const featureStatus = () => request.get({ url: '/sysParameter/feature/status' })

export const authStatus = () => request.get({ url: '/setting/authentication/status' })
