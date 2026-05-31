import { interactiveStoreWithOut } from '@/store/modules/interactive'
import {
  INTERACTIVE_PERMISSION_ORDER,
  normalizePermissionType,
  type VisualizationPermissionType
} from '@/utils/visualizationResource'
const interactiveStore = interactiveStoreWithOut()

type PermissionCapability = 'view' | 'use' | 'export' | 'manage' | 'authorize'
type PermissionCheckItem = {
  resourceType: VisualizationPermissionType
  capability?: PermissionCapability
}
type PermissionDirectiveBinding = {
  value?: unknown
}
type PermissionDirectiveElement = {
  parentNode?: {
    removeChild?: (child: unknown) => void
  } | null
}

const capabilityCheckMap: Record<PermissionCapability, string> = {
  view: 'canView',
  use: 'canUse',
  export: 'canExport',
  manage: 'canManage',
  authorize: 'canAuthorize'
}

const parsePermission = (rawPermission: string): PermissionCheckItem | undefined => {
  if (!rawPermission) {
    return undefined
  }
  const [rawResourceType, rawCapability] = rawPermission.split(':')
  const resourceType = normalizePermissionType(rawResourceType)
  if (!resourceType) {
    return undefined
  }
  if (!rawCapability) {
    return { resourceType }
  }
  if (!(rawCapability in capabilityCheckMap)) {
    return undefined
  }
  return {
    resourceType,
    capability: rawCapability as PermissionCapability
  }
}

export const checkPermission = (
  el: PermissionDirectiveElement,
  binding: PermissionDirectiveBinding
) => {
  const { value } = binding
  const data = interactiveStore.getData
  const permissionData: Partial<
    Record<
      VisualizationPermissionType,
      {
        menuAuth?: boolean
        anyManage?: boolean
      }
    >
  > = {}
  INTERACTIVE_PERMISSION_ORDER.forEach((item, index) => {
    permissionData[item] = data[index]
  })
  if (value && value instanceof Array) {
    const needPermissions = value
      .map(item => parsePermission(item))
      .filter((item): item is PermissionCheckItem => item !== undefined)
    // 满足指令中的每个权限才可放行 而不是 满足任意一个即可
    const hasPermission =
      needPermissions.length > 0 &&
      needPermissions.every(needPermission => {
        const currentPermission = permissionData?.[needPermission.resourceType]
        if (!currentPermission?.menuAuth) {
          return false
        }
        if (!needPermission.capability) {
          return currentPermission['anyManage']
        }
        const capabilities = interactiveStore.getResourceCapabilities(needPermission.resourceType)
        const capabilityKey = capabilityCheckMap[needPermission.capability]
        const result = currentPermission && capabilities && capabilities[capabilityKey]
        return result
      })
    if (!hasPermission) {
      el.parentNode && el.parentNode.removeChild?.(el)
    }
  } else {
    throw new Error(`使用方式： v-permission="['panel']"`)
  }
}
