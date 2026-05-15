export const dsTypes = [
  {
    type: 'mysql',
    name: 'MySQL',
    catalog: 'OLTP',
    extraParams:
      'characterEncoding=UTF-8&connectTimeout=5000&useSSL=false&allowPublicKeyRetrieval=true'
  },
  {
    type: 'pg',
    name: 'PostgreSQL',
    catalog: 'OLTP',
    extraParams: ''
  }
]

export const typeList = ['OLTP']
export const nameMap = {
  OLTP: 'OLTP'
}

export interface Configuration {
  dataBase: string
  jdbcUrl: string
  urlType: string
  connectionType: string
  schema: string
  extraParams: string
  username: string
  password: string
  host: string
  authMethod: string
  port: string
  initialPoolSize: string
  minPoolSize: string
  maxPoolSize: string
  queryTimeout: string
  useSSH: boolean
  sshHost: string
  sshPort: string
  sshUserName: string
  sshType: string
  sshPassword: string
  sslCA: string
  sslCert: string
  sslKey: string
}

export interface ApiConfiguration {
  id: string
  name: string
  type: string
  deTableName: string
  method: string
  copy: boolean
  url: string
  status: string
  useJsonPath: boolean
  serialNumber: number
}

export interface SyncSetting {
  id: string
  updateType: string
  syncRate: string
  simpleCronValue: number
  simpleCronType: string
  startTime: number
  endTime: number
  endLimit: string
  cron: string
}

export interface Node {
  name: string
  createBy: string
  creator: string
  copy: boolean
  createTime: string
  id: number | string
  size: number
  description: string
  type: string
  nodeType: string
  fileName: string
  syncSetting?: SyncSetting
  editType?: number
  configuration?: Configuration
  apiConfiguration?: ApiConfiguration[]
  paramsConfiguration?: ApiConfiguration[]
  weight?: number
  lastSyncTime?: number | string
}
