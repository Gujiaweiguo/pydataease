import { interactiveStoreWithOut } from '@/store/modules/interactive'
import {
  INTERACTIVE_PERMISSION_ORDER,
  normalizePermissionType,
  type VisualizationPermissionType
} from '@/utils/visualizationResource'
const interactiveStore = interactiveStoreWithOut()

export const checkPermission = (el, binding) => {
  const { value } = binding
  const data = interactiveStore.getData
  const permissionData = {}
  INTERACTIVE_PERMISSION_ORDER.forEach((item, index) => {
    permissionData[item] = data[index]
  })
  if (value && value instanceof Array) {
    const needPermissions = value
      .map(item => normalizePermissionType(item))
      .filter((item): item is VisualizationPermissionType => item !== undefined)
    // 满足指令中的每个权限才可放行 而不是 满足任意一个即可
    const hasPermission = needPermissions.every(needP => {
      const result =
        permissionData &&
        permissionData[needP] &&
        permissionData[needP]['menuAuth'] &&
        permissionData[needP]['anyManage']
      return result
    })
    if (!hasPermission) {
      el.parentNode && el.parentNode.removeChild(el)
    }
  } else {
    throw new Error(`使用方式： v-permission="['panel']"`)
  }
}
