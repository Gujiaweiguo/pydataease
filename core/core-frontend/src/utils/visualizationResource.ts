export type VisualizationCanonicalType = 'dashboard' | 'dataV' | 'dataset' | 'datasource'
export type VisualizationPermissionType = 'panel' | 'screen' | 'dataset' | 'datasource'

type ShortcutRowLike = Record<string, any>

export interface NormalizedShortcutRow {
  type?: string
  resourceId?: string | number
  autoPwd?: boolean
  ticketRequire?: boolean
  creator?: string
  lastEditor?: string
  lastEditTime?: string | number
  extFlag?: number
  extFlag1?: number
  favorite?: boolean
}

export interface InteractivePermissionLike {
  menuAuth?: boolean
  rootManage?: boolean
  anyManage?: boolean
  capabilities?: {
    canView?: boolean
    canUse?: boolean
    canExport?: boolean
    canManage?: boolean
    canAuthorize?: boolean
  }
}

export interface TemplateCreateAuthLike {
  PANEL?: boolean
  SCREEN?: boolean
}

const CANVAS_ALIAS_MAP: Record<string, VisualizationCanonicalType> = {
  dashboard: 'dashboard',
  panel: 'dashboard',
  PANEL: 'dashboard',
  datav: 'dataV',
  dataV: 'dataV',
  screen: 'dataV',
  SCREEN: 'dataV',
  dataset: 'dataset',
  datasource: 'datasource'
}

const PERMISSION_ALIAS_MAP: Record<string, VisualizationPermissionType> = {
  dashboard: 'panel',
  panel: 'panel',
  PANEL: 'panel',
  datav: 'screen',
  dataV: 'screen',
  screen: 'screen',
  SCREEN: 'screen',
  dataset: 'dataset',
  datasource: 'datasource'
}

export const INTERACTIVE_PERMISSION_ORDER: VisualizationPermissionType[] = [
  'panel',
  'screen',
  'dataset',
  'datasource'
]

export const INTERACTIVE_CANVAS_ORDER: VisualizationCanonicalType[] = [
  'dashboard',
  'dataV',
  'dataset',
  'datasource'
]

export const normalizeCanvasType = (
  rawValue?: string | null
): VisualizationCanonicalType | undefined => {
  if (!rawValue) {
    return undefined
  }
  return CANVAS_ALIAS_MAP[rawValue]
}

export const normalizePermissionType = (
  rawValue?: string | null
): VisualizationPermissionType | undefined => {
  if (!rawValue) {
    return undefined
  }
  return PERMISSION_ALIAS_MAP[rawValue]
}

export const getInteractiveIndex = (rawValue?: string | null): number => {
  const normalized = normalizeCanvasType(rawValue)
  if (!normalized) {
    return -1
  }
  return INTERACTIVE_CANVAS_ORDER.indexOf(normalized)
}

export const isDashboardLike = (rawValue?: string | null): boolean =>
  normalizeCanvasType(rawValue) === 'dashboard'

export const isScreenLike = (rawValue?: string | null): boolean =>
  normalizeCanvasType(rawValue) === 'dataV'

export const isVisualizationLike = (rawValue?: string | null): boolean => {
  const normalized = normalizeCanvasType(rawValue)
  return normalized === 'dashboard' || normalized === 'dataV'
}

export const getVisualizationRoute = (rawValue?: string | null): string | undefined => {
  if (isDashboardLike(rawValue)) {
    return '/panel/index'
  }
  if (isScreenLike(rawValue)) {
    return '/screen/index'
  }
  return undefined
}

export const toStoreResourceType = (rawValue?: string | null): string | undefined => {
  const normalized = normalizePermissionType(rawValue)
  if (normalized === 'panel' || normalized === 'screen') {
    return normalized
  }
  return rawValue ?? undefined
}

export const hasCreatePermission = (permission?: InteractivePermissionLike): boolean => {
  return !!permission?.menuAuth && !!permission?.rootManage
}

export const normalizeTemplateType = (rawValue?: string | null): 'PANEL' | 'SCREEN' | undefined => {
  if (isDashboardLike(rawValue)) {
    return 'PANEL'
  }
  if (isScreenLike(rawValue)) {
    return 'SCREEN'
  }
  if (rawValue === 'PANEL' || rawValue === 'SCREEN') {
    return rawValue
  }
  return undefined
}

export const hasTemplateCreatePermission = (
  createAuth: TemplateCreateAuthLike | undefined,
  templateType?: string | null
): boolean => {
  const normalizedType = normalizeTemplateType(templateType)
  if (!normalizedType) {
    return false
  }
  return !!createAuth?.[normalizedType]
}

export const isScreenTemplateType = (templateType?: string | null): boolean => {
  return normalizeTemplateType(templateType) === 'SCREEN'
}

export const matchesTemplateType = (
  activeTemplateType?: string | null,
  templateType?: string | null
): boolean => {
  if (activeTemplateType === 'all') {
    return true
  }
  const normalizedActiveTemplateType = normalizeTemplateType(activeTemplateType)
  const normalizedTemplateType = normalizeTemplateType(templateType)
  return !!normalizedActiveTemplateType && normalizedActiveTemplateType === normalizedTemplateType
}

export const normalizeShortcutRow = <T extends ShortcutRowLike>(
  row: T
): T & NormalizedShortcutRow => {
  if (!row) {
    return row
  }
  return {
    ...row,
    type: normalizeCanvasType(row.type) ?? row.type,
    resourceId: row.resourceId ?? row.resource_id ?? row.id,
    autoPwd: row.autoPwd ?? row.auto_pwd,
    ticketRequire: row.ticketRequire ?? row.ticket_require,
    creator: row.creator ?? row.createBy ?? row.create_by,
    lastEditor: row.lastEditor ?? row.updateBy ?? row.update_by,
    lastEditTime: row.lastEditTime ?? row.updateTime ?? row.update_time ?? row.time,
    extFlag: row.extFlag ?? row.extraFlag ?? row.extra_flag ?? row.ext,
    extFlag1: row.extFlag1 ?? row.extraFlag1 ?? row.extra_flag1,
    favorite: row.favorite ?? row.storeFlag
  }
}
