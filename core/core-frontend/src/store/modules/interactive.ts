import { defineStore } from 'pinia'
import { store } from '@/store'
import { queryTreeApi, queryBusiTreeApi } from '@/api/visualization/dataVisualization'
import { getDatasetTree } from '@/api/dataset'
import { listDatasources } from '@/api/datasource'
import type { BusiTreeRequest, BusiTreeNode } from '@/models/tree/TreeNode'
import { pathValid } from '@/store/modules/permission'
import { useCache } from '@/hooks/web/useCache'
import { useAppStoreWithOut } from '@/store/modules/app'
import {
  getInteractiveIndex,
  INTERACTIVE_CANVAS_ORDER,
  INTERACTIVE_PERMISSION_ORDER,
  normalizePermissionType
} from '@/utils/visualizationResource'
const appStore = useAppStoreWithOut()
const { wsCache } = useCache()

export interface ResourceCapabilities {
  canView: boolean
  canUse: boolean
  canExport: boolean
  canManage: boolean
  canAuthorize: boolean
}

export interface InnerInteractive {
  rootManage: boolean
  anyManage: boolean
  treeNodes: BusiTreeNode[]
  leafNodeCount: number
  menuAuth: boolean
  capabilities: ResourceCapabilities
}

interface InteractiveState {
  data: Record<number, InnerInteractive>
}

const apiMap = [queryTreeApi, queryTreeApi, getDatasetTree, listDatasources]

const createEmptyCapabilities = (): ResourceCapabilities => ({
  canView: false,
  canUse: false,
  canExport: false,
  canManage: false,
  canAuthorize: false
})

export const deriveCapabilities = (weight = 0): ResourceCapabilities => ({
  canView: weight >= 1,
  canUse: weight >= 2,
  canExport: weight >= 4,
  canManage: weight >= 7,
  canAuthorize: weight >= 9
})

const mergeCapabilities = (
  base: ResourceCapabilities,
  current: ResourceCapabilities
): ResourceCapabilities => ({
  canView: base.canView || current.canView,
  canUse: base.canUse || current.canUse,
  canExport: base.canExport || current.canExport,
  canManage: base.canManage || current.canManage,
  canAuthorize: base.canAuthorize || current.canAuthorize
})

export const interactiveStore = defineStore('interactive', {
  state: (): InteractiveState => ({
    data: {}
  }),
  getters: {
    getPanel(): InnerInteractive {
      return this.data[0]
    },
    getScreen(): InnerInteractive {
      return this.data[1]
    },
    getDataset(): InnerInteractive {
      return this.data[2]
    },
    getDatasource(): InnerInteractive {
      return this.data[3]
    },
    getData(): InteractiveState {
      return this.data
    },
    getResourceCapabilities(): (resourceType?: string | null) => ResourceCapabilities {
      return resourceType => {
        const normalizedType = normalizePermissionType(resourceType)
        if (!normalizedType) {
          return createEmptyCapabilities()
        }
        const index = INTERACTIVE_PERMISSION_ORDER.indexOf(normalizedType)
        return this.data[index]?.capabilities || createEmptyCapabilities()
      }
    }
  },
  actions: {
    async setInteractive(param: BusiTreeRequest, resParam?: BusiTreeNode[] | null) {
      const flag = getInteractiveIndex(param.busiFlag)
      if (flag < 0) {
        return []
      }
      if (!hasMenuAuth(flag) && !window.DataEaseBi && !appStore.getIsIframe) {
        const tempData: InnerInteractive = {
          rootManage: false,
          anyManage: false,
          treeNodes: [],
          leafNodeCount: 0,
          menuAuth: false,
          capabilities: createEmptyCapabilities()
        }
        this.data[flag] = tempData
        if (flag === 0) {
          wsCache.set('panel-weight', {})
        }
        if (flag === 1) {
          wsCache.set('screen-weight', {})
        }
        return []
      }
      let res = resParam
      if (!resParam) {
        const method = apiMap[flag]
        res = await method(param)
      }
      this.data[flag] = convertInteractive(res as BusiTreeNode[] | null | undefined)
      if (flag === 0) {
        wsCache.set('panel-weight', convertLocalStorage(this.data[flag]))
      }
      if (flag === 1) {
        wsCache.set('screen-weight', convertLocalStorage(this.data[flag]))
      }
      return res
    },
    async initInteractive(refresh?: boolean) {
      if (refresh) {
        await this.loadBusiInteractive()
        return
      }
      let index = 4
      while (index--) {
        if (!this.data[index] || refresh) {
          const param: BusiTreeRequest = {
            busiFlag: INTERACTIVE_CANVAS_ORDER[index]
          }
          await this.setInteractive(param)
        }
      }
    },
    async loadBusiInteractive() {
      const param = {}
      for (let i = 0; i < INTERACTIVE_CANVAS_ORDER.length; i++) {
        const key = INTERACTIVE_CANVAS_ORDER[i]
        if (window.DataEaseBi || appStore.getIsIframe || hasMenuAuth(i)) {
          param[key] = { busiFlag: key }
        }
      }
      const data = await queryBusiTreeApi(param)
      for (const busiKey in data) {
        const res = data[busiKey]
        this.setInteractive(param[busiKey], res)
      }
    },
    clear() {
      this.data = {}
      wsCache.set('panel-weight', {})
      wsCache.set('screen-weight', {})
    }
  }
})

export const interactiveStoreWithOut = () => interactiveStore(store)

const convertInteractive = (list?: BusiTreeNode[] | null): InnerInteractive => {
  if (!list || !list.length) {
    return {
      rootManage: false,
      anyManage: false,
      treeNodes: [],
      leafNodeCount: 0,
      menuAuth: true,
      capabilities: createEmptyCapabilities()
    }
  }
  const result: InnerInteractive = {
    rootManage: list[0]['weight'] >= 7,
    anyManage: false,
    treeNodes: list,
    leafNodeCount: 0,
    menuAuth: true,
    capabilities: createEmptyCapabilities()
  }
  const stack: BusiTreeNode[] = [...list]
  let leafNodeCount = 0
  while (stack.length) {
    const node = stack.pop()
    if (!node) {
      continue
    }
    const nodeCapabilities = deriveCapabilities(node?.['weight'])
    result.capabilities = mergeCapabilities(result.capabilities, nodeCapabilities)
    if (!node['leaf'] && nodeCapabilities.canManage) {
      result.anyManage = true
      // break
    }
    if (node['leaf'] && node['weight']) {
      ++leafNodeCount
    }
    if (node?.children?.length) {
      node.children.forEach((kid: BusiTreeNode) => {
        stack.push(kid)
      })
    }
  }
  result.leafNodeCount = leafNodeCount
  return result
}

const hasMenuAuth = (flag: number): boolean => {
  const permissionType = INTERACTIVE_PERMISSION_ORDER[flag]
  let path = '/panel/index'
  if (permissionType === 'screen') {
    path = '/screen/index'
  } else if (permissionType === 'dataset') {
    path = '/data/dataset'
  } else if (permissionType === 'datasource') {
    path = '/data/datasource'
  }
  const valid = pathValid(path)
  return valid
}

const convertLocalStorage = (data?: InnerInteractive) => {
  if (!data?.leafNodeCount) {
    return {}
  }
  const result = {}
  const treeNodes = data.treeNodes
  const stack: BusiTreeNode[] = [...treeNodes]
  while (stack.length) {
    const node = stack.pop()
    if (!node) {
      continue
    }
    if (node.leaf) {
      const { id, weight } = node
      result[id] = weight
    }
    if (node.children?.length) {
      node.children.forEach((kid: BusiTreeNode) => {
        stack.push(kid)
      })
    }
  }
  return result
}
