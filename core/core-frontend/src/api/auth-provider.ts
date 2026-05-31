import request from '@/config/axios'

export interface AuthProvider {
  id: number
  name: string
  type: string
  config: Record<string, any> | null
  claimMapping: Record<string, string> | null
  enabled: boolean
  isDefault: boolean
  oid: number | null
  createTime: string | null
  updateTime: string | null
}

export interface AuthProviderCreateRequest {
  name: string
  type: string
  config?: Record<string, any> | null
  claimMapping?: Record<string, string> | null
  enabled?: boolean
  isDefault?: boolean
}

export interface AuthProviderToggleRequest {
  enabled: boolean
}

export interface AuthProviderCallbackRequest {
  code: string
  state: string
  redirect_uri: string
}

export interface AuthProviderTestRequest {
  credentials: Record<string, any>
}

export const authProviderList = () => request.get({ url: '/auth-provider/list' })

export const authProviderGet = (id: number) => request.get({ url: `/auth-provider/${id}` })

export const authProviderCreate = (data: AuthProviderCreateRequest) =>
  request.post({ url: '/auth-provider/create', data })

export const authProviderUpdate = (id: number, data: AuthProviderCreateRequest) =>
  request.put({ url: `/auth-provider/${id}`, data })

export const authProviderDelete = (id: number) => request.delete({ url: `/auth-provider/${id}` })

export const authProviderToggle = (id: number, data: AuthProviderToggleRequest) =>
  request.post({ url: `/auth-provider/${id}/toggle`, data })

export const authProviderSetDefault = (id: number) =>
  request.post({ url: `/auth-provider/${id}/default` })

export const authProviderCallback = (id: number, data: AuthProviderCallbackRequest) =>
  request.post({ url: `/auth-provider/${id}/callback`, data })

export const authProviderTest = (id: number, data: AuthProviderTestRequest) =>
  request.post({ url: `/auth-provider/${id}/test`, data })

// Public APIs (no auth required)
export const authStatusApi = () => request.get({ url: '/setting/authentication/status' })

export const authProviderAuthorizeApi = (id: number, redirectUri: string) =>
  request.get({ url: `/auth-provider/${id}/authorize`, params: { redirect_uri: redirectUri } })

export const authProviderDirectLoginApi = (id: number, credentials: Record<string, any>) =>
  request.post({ url: `/auth-provider/${id}/login`, data: { credentials } })
