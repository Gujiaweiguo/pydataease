<template>
  <div class="permission-management-page">
    <div class="page-header">
      <p class="router-title">权限管理</p>
      <div class="toolbar">
        <el-input
          v-model="keyword"
          clearable
          placeholder="搜索角色名称"
          style="width: 240px"
          @keyup.enter="loadRoles"
        />
        <el-button @click="loadRoles">查询</el-button>
        <el-button
          v-if="activeTab === 'role'"
          type="primary"
          :loading="saveLoading"
          :disabled="!currentRole || permissionReadonly"
          @click="handleSave"
        >
          保存权限
        </el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="permission-tabs">
      <el-tab-pane label="角色资源权限" name="role">
        <div class="page-layout">
          <div class="page-body role-list-panel" v-loading="roleLoading">
            <div class="panel-title">角色列表</div>
            <el-table
              :data="roles"
              border
              highlight-current-row
              row-key="id"
              @current-change="handleRoleSelect"
            >
              <el-table-column prop="name" label="角色名称" min-width="140" />
              <el-table-column label="类型" width="110">
                <template #default="scope">
                  <el-tag :type="scope.row.type === 0 ? 'info' : 'success'">
                    {{ scope.row.type === 0 ? '内置角色' : '自定义角色' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column
                prop="description"
                label="描述"
                min-width="180"
                show-overflow-tooltip
              />
            </el-table>
          </div>

          <div class="page-body permission-panel" v-loading="treeLoading || permissionLoading">
            <template v-if="currentRole">
              <div class="detail-header">
                <div>
                  <div class="detail-title">
                    <h3>{{ currentRole.name }}</h3>
                    <el-tag :type="currentRole.type === 0 ? 'info' : 'success'">
                      {{ currentRole.type === 0 ? '内置角色' : '自定义角色' }}
                    </el-tag>
                    <el-tag v-if="permissionReadonly" type="warning">只读模式</el-tag>
                    <el-tag v-if="permissionRoot" type="success">超级管理员</el-tag>
                  </div>
                  <p>{{ currentRole.description || '为当前角色配置菜单可见性与资源权限级别。' }}</p>
                </div>
                <div class="status-tip">
                  <span>{{
                    permissionReadonly
                      ? '当前账号仅可查看授权结果'
                      : '勾选菜单并选择资源权限后保存生效'
                  }}</span>
                </div>
              </div>

              <div class="permission-section">
                <div class="section-header">
                  <div>
                    <h4>菜单权限</h4>
                    <p>勾选后角色可访问对应菜单；半选节点会自动保留父级路径。</p>
                  </div>
                </div>
                <div class="tree-shell">
                  <el-tree
                    ref="menuTreeRef"
                    :data="menuTreeDisplay"
                    :props="treeProps"
                    node-key="id"
                    show-checkbox
                    default-expand-all
                    :expand-on-click-node="false"
                    :check-on-click-node="false"
                    empty-text="暂无菜单数据"
                  />
                </div>
              </div>

              <div class="resource-section-grid">
                <div
                  v-for="section in resourceSections"
                  :key="section.flag"
                  class="permission-section resource-card"
                >
                  <div class="section-header resource-header">
                    <div>
                      <h4>{{ section.label }}</h4>
                      <p>{{ section.description }}</p>
                    </div>
                    <el-tag type="info">{{ section.rows.length }} 项资源</el-tag>
                  </div>

                  <el-table :data="section.rows" border row-key="id" max-height="320">
                    <el-table-column label="资源名称" min-width="240">
                      <template #default="scope">
                        <div
                          class="resource-name"
                          :style="{ paddingLeft: `${12 + scope.row.depth * 18}px` }"
                        >
                          <span
                            class="resource-bullet"
                            :class="{ 'resource-bullet-folder': !scope.row.leaf }"
                          />
                          <span>{{ scope.row.name }}</span>
                        </div>
                      </template>
                    </el-table-column>
                    <el-table-column label="权限级别" width="220">
                      <template #default="scope">
                        <el-select
                          v-model="resourceSelections[section.flag][scope.row.id]"
                          clearable
                          placeholder="未授权"
                          style="width: 100%"
                          :disabled="permissionReadonly"
                        >
                          <el-option
                            v-for="option in permissionOptions[section.flag]"
                            :key="option.value"
                            :label="option.label"
                            :value="option.value"
                          />
                        </el-select>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </div>
            </template>

            <el-empty v-else description="请选择左侧角色配置权限" />
          </div>
        </div>
      </el-tab-pane>
      <el-tab-pane label="行列权限" name="row-column">
        <RowColumnPermission />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script lang="ts" setup>
import { computed, nextTick, onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus-secondary'
import {
  busiPerSaveApi,
  menuPerApi,
  menuPerSaveApi,
  menuTreeApi,
  queryRoleApi,
  resourcePerApi,
  resourceTreeApi
} from '@/api/auth'
import RowColumnPermission from './RowColumnPermission.vue'

type ResourceFlag = 'dashboard' | 'screen' | 'dataset' | 'datasource'

interface RoleItem {
  id: number
  name: string
  description?: string
  type: number
}

interface ResourceNode {
  id: string | number
  name: string
  leaf?: boolean
  disabled?: boolean
  children?: ResourceNode[]
}

interface PermissionItem {
  id: string | number
  weight: number
  ext?: number
}

interface PermissionResponse {
  root?: boolean
  readonly?: boolean
  permissions?: PermissionItem[]
}

interface ResourceRow {
  id: number
  name: string
  depth: number
  leaf: boolean
}

interface ResourceSection {
  flag: ResourceFlag
  label: string
  description: string
  rows: ResourceRow[]
}

const RESOURCE_FLAGS: ResourceFlag[] = ['dashboard', 'screen', 'dataset', 'datasource']

const RESOURCE_META: Record<ResourceFlag, { label: string; description: string }> = {
  dashboard: {
    label: '仪表板权限',
    description: '为仪表板配置查看、导出、管理或授权级别。'
  },
  screen: {
    label: '大屏权限',
    description: '控制大屏资源的浏览、导出、管理与再次授权能力。'
  },
  dataset: {
    label: '数据集权限',
    description: '控制数据集的使用、管理与授权能力。'
  },
  datasource: {
    label: '数据源权限',
    description: '控制数据源的使用、管理与授权能力。'
  }
}

const permissionOptions: Record<ResourceFlag, Array<{ label: string; value: number }>> = {
  dashboard: [
    { label: '查看', value: 1 },
    { label: '导出', value: 4 },
    { label: '管理', value: 7 },
    { label: '授权', value: 9 }
  ],
  screen: [
    { label: '查看', value: 1 },
    { label: '导出', value: 4 },
    { label: '管理', value: 7 },
    { label: '授权', value: 9 }
  ],
  dataset: [
    { label: '使用', value: 2 },
    { label: '管理', value: 7 },
    { label: '授权', value: 9 }
  ],
  datasource: [
    { label: '使用', value: 2 },
    { label: '管理', value: 7 },
    { label: '授权', value: 9 }
  ]
}

const treeProps = { label: 'name', children: 'children', disabled: 'disabled' }

const activeTab = ref('role')
const keyword = ref('')
const roleLoading = ref(false)
const treeLoading = ref(false)
const permissionLoading = ref(false)
const saveLoading = ref(false)
const roles = ref<RoleItem[]>([])
const currentRole = ref<RoleItem | null>(null)
const permissionReadonly = ref(false)
const permissionRoot = ref(false)
const menuTree = ref<ResourceNode[]>([])
const menuCheckedKeys = ref<Array<string | number>>([])
const resourceTrees = reactive<Record<ResourceFlag, ResourceNode[]>>({
  dashboard: [],
  screen: [],
  dataset: [],
  datasource: []
})
const resourceSelections = reactive<Record<ResourceFlag, Record<number, number | undefined>>>({
  dashboard: {},
  screen: {},
  dataset: {},
  datasource: {}
})
const menuTreeRef = ref<any>()

const menuTreeDisplay = computed(() => decorateTree(menuTree.value, permissionReadonly.value))

const resourceSections = computed<ResourceSection[]>(() =>
  RESOURCE_FLAGS.map(flag => ({
    flag,
    label: RESOURCE_META[flag].label,
    description: RESOURCE_META[flag].description,
    rows: flattenResourceRows(resourceTrees[flag])
  }))
)

const loadRoles = async () => {
  roleLoading.value = true
  try {
    const res = await queryRoleApi({ keyword: keyword.value.trim() || undefined })
    roles.value = res.data || []
    if (!roles.value.length) {
      currentRole.value = null
      resetPermissionState()
      return
    }

    const nextRole =
      roles.value.find(role => role.id === currentRole.value?.id) || roles.value[0] || null

    if (nextRole) {
      await handleRoleSelect(nextRole)
    }
  } finally {
    roleLoading.value = false
  }
}

const loadBaseTrees = async () => {
  treeLoading.value = true
  try {
    const [menuRes, ...resourceRes] = await Promise.all([
      menuTreeApi(),
      ...RESOURCE_FLAGS.map(flag => resourceTreeApi(flag))
    ])

    menuTree.value = menuRes.data || []
    RESOURCE_FLAGS.forEach((flag, index) => {
      resourceTrees[flag] = resourceRes[index].data || []
    })
  } finally {
    treeLoading.value = false
  }
}

const handleRoleSelect = async (role: RoleItem | undefined | null) => {
  if (!role) {
    return
  }
  currentRole.value = role
  await loadRolePermissions(role)
}

const loadRolePermissions = async (role: RoleItem) => {
  permissionLoading.value = true
  try {
    const [menuRes, ...resourceRes] = await Promise.all([
      menuPerApi({ id: role.id }),
      ...RESOURCE_FLAGS.map(flag => resourcePerApi({ id: role.id, type: 1, flag }))
    ])

    const menuData = (menuRes.data || {}) as PermissionResponse
    permissionReadonly.value = Boolean(menuData.readonly)
    permissionRoot.value = Boolean(menuData.root)
    menuCheckedKeys.value = (menuData.permissions || [])
      .filter(item => Number(item.weight) > 0)
      .map(item => String(item.id))

    RESOURCE_FLAGS.forEach((flag, index) => {
      applyResourceSelections(flag, (resourceRes[index].data || {}) as PermissionResponse)
    })

    await nextTick()
    menuTreeRef.value?.setCheckedKeys(menuCheckedKeys.value)
  } finally {
    permissionLoading.value = false
  }
}

const applyResourceSelections = (flag: ResourceFlag, response: PermissionResponse) => {
  const nextSelections: Record<number, number | undefined> = {}
  ;(response.permissions || []).forEach(item => {
    const resourceId = Number(item.id)
    if (!Number.isNaN(resourceId) && Number(item.weight) > 0) {
      nextSelections[resourceId] = Number(item.weight)
    }
  })
  resourceSelections[flag] = nextSelections
}

const handleSave = async () => {
  if (!currentRole.value) {
    ElMessage.warning('请先选择角色')
    return
  }
  if (permissionReadonly.value) {
    ElMessage.warning('当前账号无权修改授权配置')
    return
  }

  const checkedKeys = (menuTreeRef.value?.getCheckedKeys(false) || []).map(key => String(key))
  const halfCheckedKeys = (menuTreeRef.value?.getHalfCheckedKeys?.() || []).map(key => String(key))
  const menuPermissionIds = Array.from(new Set([...checkedKeys, ...halfCheckedKeys]))

  saveLoading.value = true
  try {
    await Promise.all([
      menuPerSaveApi({
        id: currentRole.value.id,
        permissions: menuPermissionIds.map(id => ({
          id: Number(id),
          weight: 1,
          ext: 0
        }))
      }),
      ...RESOURCE_FLAGS.map(flag =>
        busiPerSaveApi({
          id: currentRole.value!.id,
          type: 1,
          flag,
          permissions: Object.entries(resourceSelections[flag])
            .filter(([, weight]) => weight !== undefined && weight !== null)
            .map(([id, weight]) => ({
              id: Number(id),
              weight: Number(weight),
              ext: 0
            }))
        })
      )
    ])

    ElMessage.success('权限保存成功')
    await loadRolePermissions(currentRole.value)
  } finally {
    saveLoading.value = false
  }
}

const resetPermissionState = () => {
  permissionReadonly.value = false
  permissionRoot.value = false
  menuCheckedKeys.value = []
  RESOURCE_FLAGS.forEach(flag => {
    resourceSelections[flag] = {}
  })
  nextTick(() => {
    menuTreeRef.value?.setCheckedKeys([])
  })
}

const decorateTree = (nodes: ResourceNode[], disabled: boolean): ResourceNode[] => {
  return nodes.map(node => ({
    ...node,
    disabled,
    children: node.children?.length ? decorateTree(node.children, disabled) : []
  }))
}

const flattenResourceRows = (nodes: ResourceNode[], depth = 0): ResourceRow[] => {
  const rows: ResourceRow[] = []
  nodes.forEach(node => {
    if (String(node.id) === '0') {
      rows.push(...flattenResourceRows(node.children || [], depth))
      return
    }

    rows.push({
      id: Number(node.id),
      name: node.name,
      depth,
      leaf: Boolean(node.leaf ?? !node.children?.length)
    })

    if (node.children?.length) {
      rows.push(...flattenResourceRows(node.children, depth + 1))
    }
  })
  return rows
}

onMounted(async () => {
  await loadBaseTrees()
  await loadRoles()
})
</script>

<style scoped lang="less">
.permission-management-page {
  .page-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    gap: 16px;
  }

  .router-title {
    margin: 0;
    color: #1f2329;
    font-family: var(--de-custom_font, 'PingFang');
    font-size: 20px;
    font-weight: 500;
    line-height: 28px;
  }

  .toolbar {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }

  .page-layout {
    display: grid;
    grid-template-columns: minmax(340px, 32%) minmax(0, 1fr);
    gap: 16px;
    min-height: calc(100vh - 176px);
  }

  .page-body {
    padding: 16px;
    background: var(--ContentBG, #ffffff);
    border-radius: 12px;
    overflow: hidden;
  }

  .panel-title {
    margin-bottom: 12px;
    color: #1f2329;
    font-size: 16px;
    font-weight: 500;
    line-height: 24px;
  }

  .permission-panel {
    overflow-y: auto;
  }

  .detail-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 16px;

    p {
      margin: 8px 0 0;
      color: #646a73;
      line-height: 22px;
    }
  }

  .detail-title {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;

    h3 {
      margin: 0;
      color: #1f2329;
      font-size: 18px;
      line-height: 26px;
    }
  }

  .status-tip {
    display: flex;
    align-items: center;
    min-height: 32px;
    padding: 0 12px;
    color: #3f4854;
    background: #f5f7fa;
    border-radius: 8px;
    white-space: nowrap;
  }

  .permission-section {
    margin-bottom: 16px;
    border: 1px solid #ebedf0;
    border-radius: 12px;
    background: linear-gradient(
      180deg,
      rgba(245, 247, 250, 0.72) 0%,
      rgba(255, 255, 255, 0.96) 100%
    );
  }

  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 16px 16px 12px;

    h4 {
      margin: 0;
      color: #1f2329;
      font-size: 16px;
      font-weight: 500;
      line-height: 24px;
    }

    p {
      margin: 4px 0 0;
      color: #646a73;
      font-size: 13px;
      line-height: 20px;
    }
  }

  .tree-shell {
    max-height: 360px;
    padding: 0 16px 16px;
    overflow: auto;
  }

  .resource-section-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
  }

  .resource-card {
    margin-bottom: 0;
    overflow: hidden;
  }

  .resource-header {
    padding-bottom: 8px;
  }

  .resource-name {
    display: flex;
    align-items: center;
    min-height: 24px;
    gap: 8px;
  }

  .resource-bullet {
    width: 8px;
    height: 8px;
    flex: 0 0 8px;
    border-radius: 999px;
    background: #b7bec8;
  }

  .resource-bullet-folder {
    background: #3370ff;
    box-shadow: 0 0 0 4px rgba(51, 112, 255, 0.14);
  }
}
</style>
