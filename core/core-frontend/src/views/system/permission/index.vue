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
          @clear="loadRoles"
        />
        <el-button @click="loadRoles">查询</el-button>
      </div>
    </div>

    <el-tabs v-model="activeTab" class="permission-tabs">
      <el-tab-pane label="菜单权限" name="menu">
        <div class="page-body page-layout" v-loading="roleLoading">
          <aside class="role-sidebar">
            <div class="sidebar-caption">角色列表</div>
            <div class="sidebar-table-wrap">
              <el-table
                class="role-table"
                :data="roles"
                border
                row-key="id"
                highlight-current-row
                :current-row-key="menuRoleId"
                height="100%"
                @current-change="handleMenuRoleSelect"
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
          </aside>

          <section class="table-panel" v-loading="treeLoading || menuPermissionLoading">
            <template v-if="menuCurrentRole">
              <div class="table-panel-header">
                <div class="panel-copy">
                  <div class="panel-title-row">
                    <h3>{{ menuCurrentRole.name }}</h3>
                    <el-tag :type="menuCurrentRole.type === 0 ? 'info' : 'success'">
                      {{ menuCurrentRole.type === 0 ? '内置角色' : '自定义角色' }}
                    </el-tag>
                    <el-tag v-if="menuPermissionReadonly" type="warning">只读模式</el-tag>
                    <el-tag v-if="menuPermissionRoot" type="success">超级管理员</el-tag>
                  </div>
                  <p>{{ menuCurrentRole.description || '为当前角色配置菜单可见性。' }}</p>
                </div>
                <div class="panel-header-actions">
                  <div class="selected-summary">
                    {{
                      menuPermissionReadonly
                        ? '当前账号仅可查看菜单授权结果'
                        : '勾选菜单并保存后立即生效'
                    }}
                  </div>
                  <el-button
                    type="primary"
                    :loading="menuSaveLoading"
                    :disabled="!menuCurrentRole || menuPermissionReadonly"
                    @click="handleMenuSave"
                  >
                    保存权限
                  </el-button>
                </div>
              </div>

              <div class="permission-section menu-section">
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
            </template>

            <el-empty v-else description="请选择左侧角色配置菜单权限" />
          </section>
        </div>
      </el-tab-pane>

      <el-tab-pane label="资源权限" name="resource">
        <div class="page-body page-layout" v-loading="roleLoading">
          <aside class="role-sidebar">
            <div class="sidebar-caption">角色列表</div>
            <div class="sidebar-table-wrap">
              <el-table
                class="role-table"
                :data="roles"
                border
                row-key="id"
                highlight-current-row
                :current-row-key="resourceRoleId"
                height="100%"
                @current-change="handleResourceRoleSelect"
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
          </aside>

          <section class="table-panel" v-loading="treeLoading || resourcePermissionLoading">
            <template v-if="resourceCurrentRole">
              <div class="table-panel-header">
                <div class="panel-copy">
                  <div class="panel-title-row">
                    <h3>{{ resourceCurrentRole.name }}</h3>
                    <el-tag :type="resourceCurrentRole.type === 0 ? 'info' : 'success'">
                      {{ resourceCurrentRole.type === 0 ? '内置角色' : '自定义角色' }}
                    </el-tag>
                    <el-tag v-if="resourcePermissionReadonly" type="warning">只读模式</el-tag>
                    <el-tag v-if="resourcePermissionRoot" type="success">超级管理员</el-tag>
                  </div>
                  <p>{{ resourceCurrentRole.description || '为当前角色配置资源权限级别。' }}</p>
                </div>
                <div class="panel-header-actions">
                  <div class="selected-summary">
                    {{
                      resourcePermissionReadonly
                        ? '当前账号仅可查看资源授权结果'
                        : '选择资源权限级别后保存生效'
                    }}
                  </div>
                  <el-button
                    type="primary"
                    :loading="resourceSaveLoading"
                    :disabled="!resourceCurrentRole || resourcePermissionReadonly"
                    @click="handleResourceSave"
                  >
                    保存权限
                  </el-button>
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
                          :disabled="resourcePermissionReadonly"
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

            <el-empty v-else description="请选择左侧角色配置资源权限" />
          </section>
        </div>
      </el-tab-pane>

      <el-tab-pane label="行列权限" name="row-column">
        <RowColumnPermission />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script lang="ts" setup>
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
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

type TabName = 'menu' | 'resource' | 'row-column'
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
  id: string
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

interface MenuTreeInstance {
  setCheckedKeys: (keys: Array<string | number>) => void
  getCheckedKeys: (leafOnly?: boolean) => Array<string | number>
  getHalfCheckedKeys: () => Array<string | number>
}

const RESOURCE_FLAGS: ResourceFlag[] = ['dashboard', 'screen', 'dataset', 'datasource']

const RESOURCE_META: Record<ResourceFlag, { label: string; description: string }> = {
  dashboard: {
    label: '仪表板权限',
    description: '控制仪表板的查看、导出（图片/PDF/模板/图表Excel/明细）、管理与授权能力。'
  },
  screen: {
    label: '大屏权限',
    description: '控制数据大屏的查看、导出、管理与授权能力。'
  },
  dataset: {
    label: '数据集权限',
    description: '控制数据集的使用、管理与授权能力。'
  },
  datasource: {
    label: '数据源权限',
    description: '控制数据源的查看（基本信息/表结构）、使用、管理与授权能力。'
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
    { label: '查看', value: 1 },
    { label: '使用', value: 2 },
    { label: '管理', value: 7 },
    { label: '授权', value: 9 }
  ]
}

const treeProps = { label: 'name', children: 'children', disabled: 'disabled' }

const activeTab = ref<TabName>('menu')
const keyword = ref('')
const roleLoading = ref(false)
const treeLoading = ref(false)
const menuPermissionLoading = ref(false)
const resourcePermissionLoading = ref(false)
const menuSaveLoading = ref(false)
const resourceSaveLoading = ref(false)
const roles = ref<RoleItem[]>([])
const menuRoleId = ref<number>()
const resourceRoleId = ref<number>()
const menuPermissionReadonly = ref(false)
const menuPermissionRoot = ref(false)
const resourcePermissionReadonly = ref(false)
const resourcePermissionRoot = ref(false)
const menuTree = ref<ResourceNode[]>([])
const menuCheckedKeys = ref<Array<string | number>>([])
const resourceTrees = reactive<Record<ResourceFlag, ResourceNode[]>>({
  dashboard: [],
  screen: [],
  dataset: [],
  datasource: []
})
const resourceSelections = reactive<Record<ResourceFlag, Record<string, number | undefined>>>({
  dashboard: {},
  screen: {},
  dataset: {},
  datasource: {}
})
const menuTreeRef = ref<MenuTreeInstance>()

const menuCurrentRole = computed(
  () => roles.value.find(role => role.id === menuRoleId.value) || null
)

const resourceCurrentRole = computed(
  () => roles.value.find(role => role.id === resourceRoleId.value) || null
)

const menuTreeDisplay = computed(() => decorateTree(menuTree.value, menuPermissionReadonly.value))

const resourceSections = computed<ResourceSection[]>(() =>
  RESOURCE_FLAGS.map(flag => ({
    flag,
    label: RESOURCE_META[flag].label,
    description: RESOURCE_META[flag].description,
    rows: flattenResourceRows(resourceTrees[flag])
  }))
)

const getNextRoleId = (roleId: number | undefined) =>
  roles.value.find(role => role.id === roleId)?.id || roles.value[0]?.id

const syncMenuTreeCheckedKeys = async () => {
  await nextTick()
  menuTreeRef.value?.setCheckedKeys(menuCheckedKeys.value)
}

const resetMenuPermissionState = () => {
  menuPermissionReadonly.value = false
  menuPermissionRoot.value = false
  menuCheckedKeys.value = []
  void syncMenuTreeCheckedKeys()
}

const resetResourcePermissionState = () => {
  resourcePermissionReadonly.value = false
  resourcePermissionRoot.value = false
  RESOURCE_FLAGS.forEach(flag => {
    resourceSelections[flag] = {}
  })
}

const loadRoles = async () => {
  roleLoading.value = true
  try {
    const res = await queryRoleApi({ keyword: keyword.value.trim() || undefined })
    roles.value = res.data || []

    if (!roles.value.length) {
      menuRoleId.value = undefined
      resourceRoleId.value = undefined
      resetMenuPermissionState()
      resetResourcePermissionState()
      return
    }

    menuRoleId.value = getNextRoleId(menuRoleId.value)
    resourceRoleId.value = getNextRoleId(resourceRoleId.value)

    await Promise.all([
      menuRoleId.value ? loadMenuPermissions(menuRoleId.value) : Promise.resolve(),
      resourceRoleId.value ? loadResourcePermissions(resourceRoleId.value) : Promise.resolve()
    ])
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

const handleMenuRoleSelect = async (role: RoleItem | undefined | null) => {
  if (!role) {
    return
  }
  menuRoleId.value = role.id
  await loadMenuPermissions(role.id)
}

const handleResourceRoleSelect = async (role: RoleItem | undefined | null) => {
  if (!role) {
    return
  }
  resourceRoleId.value = role.id
  await loadResourcePermissions(role.id)
}

const loadMenuPermissions = async (roleId: number) => {
  menuPermissionLoading.value = true
  try {
    const menuRes = await menuPerApi({ id: roleId })
    const menuData = (menuRes.data || {}) as PermissionResponse
    menuPermissionReadonly.value = Boolean(menuData.readonly)
    menuPermissionRoot.value = Boolean(menuData.root)
    menuCheckedKeys.value = (menuData.permissions || [])
      .filter(item => Number(item.weight) > 0)
      .map(item => String(item.id))

    await syncMenuTreeCheckedKeys()
  } finally {
    menuPermissionLoading.value = false
  }
}

const loadResourcePermissions = async (roleId: number) => {
  resourcePermissionLoading.value = true
  try {
    const [menuRes, ...resourceRes] = await Promise.all([
      menuPerApi({ id: roleId }),
      ...RESOURCE_FLAGS.map(flag => resourcePerApi({ id: roleId, type: 1, flag }))
    ])

    const menuData = (menuRes.data || {}) as PermissionResponse
    resourcePermissionReadonly.value = Boolean(menuData.readonly)
    resourcePermissionRoot.value = Boolean(menuData.root)

    RESOURCE_FLAGS.forEach((flag, index) => {
      applyResourceSelections(flag, (resourceRes[index].data || {}) as PermissionResponse)
    })
  } finally {
    resourcePermissionLoading.value = false
  }
}

const applyResourceSelections = (flag: ResourceFlag, response: PermissionResponse) => {
  const nextSelections: Record<string, number | undefined> = {}
  ;(response.permissions || []).forEach(item => {
    const resourceId = String(item.id)
    if (resourceId && Number(item.weight) > 0) {
      nextSelections[resourceId] = Number(item.weight)
    }
  })
  resourceSelections[flag] = nextSelections
}

const handleMenuSave = async () => {
  if (!menuCurrentRole.value) {
    ElMessage.warning('请先选择角色')
    return
  }
  if (menuPermissionReadonly.value) {
    ElMessage.warning('当前账号无权修改授权配置')
    return
  }

  const checkedKeys = (menuTreeRef.value?.getCheckedKeys(false) || []).map(key => String(key))
  const halfCheckedKeys = (menuTreeRef.value?.getHalfCheckedKeys() || []).map(key => String(key))
  const menuPermissionIds = Array.from(new Set([...checkedKeys, ...halfCheckedKeys]))

  menuSaveLoading.value = true
  try {
    await menuPerSaveApi({
      id: menuCurrentRole.value.id,
      permissions: menuPermissionIds.map(id => ({
        id: String(id),
        weight: 1,
        ext: 0
      }))
    })

    ElMessage.success('菜单权限保存成功')
    await loadMenuPermissions(menuCurrentRole.value.id)
  } finally {
    menuSaveLoading.value = false
  }
}

const handleResourceSave = async () => {
  if (!resourceCurrentRole.value) {
    ElMessage.warning('请先选择角色')
    return
  }
  if (resourcePermissionReadonly.value) {
    ElMessage.warning('当前账号无权修改授权配置')
    return
  }

  const roleId = resourceCurrentRole.value.id
  resourceSaveLoading.value = true
  try {
    await Promise.all(
      RESOURCE_FLAGS.map(flag =>
        busiPerSaveApi({
          id: roleId,
          type: 1,
          flag,
          permissions: Object.entries(resourceSelections[flag])
            .filter(([, weight]) => weight !== undefined && weight !== null)
            .map(([id, weight]) => ({
              id: String(id),
              weight: Number(weight),
              ext: 0
            }))
        })
      )
    )

    ElMessage.success('资源权限保存成功')
    await loadResourcePermissions(resourceCurrentRole.value.id)
  } finally {
    resourceSaveLoading.value = false
  }
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
      id: String(node.id),
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

watch(activeTab, async tab => {
  if (tab === 'menu') {
    await syncMenuTreeCheckedKeys()
  }
})

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
    justify-content: flex-end;
    gap: 12px;
    flex-wrap: wrap;
  }

  .page-body {
    background: var(--ContentBG, #ffffff);
    border-radius: 12px;
  }

  .page-layout {
    display: grid;
    grid-template-columns: 300px minmax(0, 1fr);
    min-height: calc(100vh - 224px);
    padding: 0;
    overflow: hidden;
  }

  .role-sidebar {
    display: flex;
    flex-direction: column;
    min-width: 0;
    padding: 16px 12px 16px 16px;
    background: var(--ContentBG, #ffffff);
    border-right: 1px solid #ebedf0;
    overflow: hidden;
  }

  .sidebar-caption {
    margin-bottom: 12px;
    color: #646a73;
    font-size: 13px;
    line-height: 20px;
  }

  .sidebar-table-wrap {
    flex: 1;
    min-height: 0;
  }

  .table-panel {
    display: flex;
    flex-direction: column;
    min-width: 0;
    padding: 16px;
    overflow: hidden;
  }

  .table-panel-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 16px;
  }

  .panel-copy {
    min-width: 0;

    p {
      margin: 6px 0 0;
      color: #646a73;
      font-size: 13px;
      line-height: 20px;
    }
  }

  .panel-title-row {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;

    h3 {
      margin: 0;
      color: #1f2329;
      font-size: 18px;
      font-weight: 500;
      line-height: 26px;
    }
  }

  .panel-header-actions {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 12px;
    flex-wrap: wrap;
  }

  .selected-summary {
    display: inline-flex;
    align-items: center;
    min-height: 32px;
    padding: 0 12px;
    color: #3f4854;
    font-size: 13px;
    background: #f5f7fa;
    border-radius: 999px;
    white-space: nowrap;
  }

  .permission-section {
    border: 1px solid #ebedf0;
    border-radius: 12px;
    background: linear-gradient(
      180deg,
      rgba(245, 247, 250, 0.72) 0%,
      rgba(255, 255, 255, 0.96) 100%
    );
  }

  .menu-section {
    flex: 1;
    min-height: 0;
    overflow: hidden;
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
    height: calc(100% - 68px);
    min-height: 420px;
    padding: 0 16px 16px;
    overflow: auto;
  }

  .resource-section-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 16px;
    overflow: auto;
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

  :deep(.permission-tabs .el-tabs__content) {
    overflow: visible;
  }

  :deep(.role-table .el-table__row.current-row > td.el-table__cell) {
    background: rgba(51, 112, 255, 0.08);
  }

  :deep(.role-table .el-table__body tr:hover > td.el-table__cell) {
    background: rgba(51, 112, 255, 0.04);
  }
}
</style>
