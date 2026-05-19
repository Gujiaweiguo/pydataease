export declare const BODY_TYPE: {
  KV: string
  FORM_DATA: string
  RAW: string
  WWW_FORM: string
  XML: string
  JSON: string
}

export declare class KeyValue {
  constructor(options?: Record<string, unknown>)
  name?: string
  value?: string
  type?: string
  files?: unknown
  enable?: boolean
  uuid?: string
  time?: unknown
  contentType?: string
}
