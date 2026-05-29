<template>
  <div class="row-column-permission-page" v-loading="pageLoading">
    <div class="page-header">
      <div>
        <h3>数据集行列权限</h3>
        <p>按数据集维护行权限、列权限与白名单，规则保存后即时生效。</p>
      </div>
      <div class="header-actions">
        <el-button @click="loadAllData">刷新</el-button>
      </div>
    </div>

    <div class="filter-card">
      <div class="filter-grid">
        <div class="filter-item dataset-select-item">
          <span class="filter-label">数据集</span>
          <el-select
            v-model="selectedDatasetId"
            filterable
            placeholder="请选择需要管理的数据集"
            style="width: 100%"
            @change="handleDatasetChange"
          >
            <el-option
              v-for="dataset in datasetOptions"
              :key="dataset.id"
              :label="dataset.name"
              :value="dataset.id"
            />
          </el-select>
        </div>
        <div class="filter-item current-dataset-item">
          <span class="filter-label">当前数据集</span>
          <div class="current-dataset-name">{{ selectedDataset?.name || '未选择数据集' }}</div>
        </div>
      </div>
    </div>

    <el-empty v-if="!selectedDatasetId" description="请选择数据集后开始配置行列权限" />

    <template v-else>
      <div class="section-card">
        <div class="section-header">
          <div>
            <h4>行权限规则</h4>
            <p>按组织、角色或用户配置 SQL 过滤条件，命中规则后仅返回满足条件的数据。</p>
          </div>
          <el-button type="primary" @click="openCreateRowDialog">新增行权限</el-button>
        </div>

        <el-table :data="rowRules" border row-key="id" empty-text="暂无行权限规则">
          <el-table-column label="目标类型" width="120">
            <template #default="scope">
              <el-tag>{{
                targetTypeLabelMap[scope.row.targetType] || scope.row.targetType
              }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="目标对象" min-width="180">
            <template #default="scope">
              <span>{{ resolveTargetName(scope.row.targetType, scope.row.targetId) }}</span>
            </template>
          </el-table-column>
          <el-table-column
            prop="filterSql"
            label="过滤条件"
            min-width="320"
            show-overflow-tooltip
          />
          <el-table-column label="状态" width="120">
            <template #default="scope">
              <el-switch
                :model-value="scope.row.enabled"
                @change="value => handleToggleRowRule(scope.row, value)"
              />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="scope">
              <el-button link type="primary" @click="openEditRowDialog(scope.row)">编辑</el-button>
              <el-button link type="danger" @click="handleDeleteRowRule(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="section-card">
        <div class="section-header">
          <div>
            <h4>列权限规则</h4>
            <p>可对字段设置禁用、脱敏或掩码动作，按用户、角色、组织维度分别维护。</p>
          </div>
          <el-button type="primary" @click="openCreateColumnDialog">新增列权限</el-button>
        </div>

        <el-table :data="columnRules" border row-key="id" empty-text="暂无列权限规则">
          <el-table-column label="字段" min-width="180">
            <template #default="scope">
              <span>{{ resolveFieldName(scope.row.fieldId) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="目标类型" width="120">
            <template #default="scope">
              <el-tag>{{
                targetTypeLabelMap[scope.row.targetType] || scope.row.targetType
              }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="目标对象" min-width="180">
            <template #default="scope">
              <span>{{ resolveTargetName(scope.row.targetType, scope.row.targetId) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="动作" width="140">
            <template #default="scope">
              <el-tag type="info">{{
                actionLabelMap[scope.row.action] || scope.row.action
              }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="120">
            <template #default="scope">
              <el-switch
                :model-value="scope.row.enabled"
                @change="value => handleToggleColumnRule(scope.row, value)"
              />
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="scope">
              <el-button link type="primary" @click="openEditColumnDialog(scope.row)"
                >编辑</el-button
              >
              <el-button link type="danger" @click="handleDeleteColumnRule(scope.row)"
                >删除</el-button
              >
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div class="section-card">
        <div class="section-header">
          <div>
            <h4>白名单管理</h4>
            <p>白名单用户可绕过当前数据集的行权限、列权限或两者。</p>
          </div>
          <el-button type="primary" @click="openCreateWhitelistDialog">新增白名单</el-button>
        </div>

        <el-table :data="datasetWhitelist" border row-key="id" empty-text="暂无白名单记录">
          <el-table-column label="用户" min-width="180">
            <template #default="scope">
              <span>{{ resolveUserName(scope.row.userId) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="作用范围" width="140">
            <template #default="scope">
              <el-tag type="success">{{
                whitelistScopeLabelMap[scope.row.scope] || scope.row.scope
              }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="创建时间" min-width="180">
            <template #default="scope">
              <span>{{ formatTimestamp(scope.row.createTime) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120" fixed="right">
            <template #default="scope">
              <el-button link type="danger" @click="handleDeleteWhitelist(scope.row)"
                >删除</el-button
              >
            </template>
          </el-table-column>
        </el-table>
      </div>
    </template>

    <el-dialog
      v-model="rowDialogVisible"
      :title="editingRowRule ? '编辑行权限规则' : '新增行权限规则'"
      width="640px"
    >
      <el-form ref="rowFormRef" :model="rowForm" :rules="rowFormRules" label-width="100px">
        <el-form-item v-if="!editingRowRule" label="目标类型" prop="targetType">
          <el-select
            v-model="rowForm.targetType"
            placeholder="请选择目标类型"
            @change="handleRowTargetTypeChange"
          >
            <el-option
              v-for="option in targetTypeOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!editingRowRule" label="目标对象" prop="targetId">
          <el-select v-model="rowForm.targetId" filterable placeholder="请选择目标对象">
            <el-option
              v-for="option in currentTargetOptions"
              :key="option.id"
              :label="option.name"
              :value="option.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-else label="目标对象">
          <div class="readonly-value">
            {{ resolveTargetName(rowForm.targetType, rowForm.targetId) }}
          </div>
        </el-form-item>
        <el-form-item label="过滤条件" prop="filterSql">
          <el-input
            v-model="rowForm.filterSql"
            type="textarea"
            :rows="4"
            placeholder="例如：owner_id = 22 或 region = 'east'"
          />
        </el-form-item>
        <el-form-item label="启用状态" prop="enabled">
          <el-switch v-model="rowForm.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rowDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="dialogLoading" @click="submitRowRule">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="columnDialogVisible"
      :title="editingColumnRule ? '编辑列权限规则' : '新增列权限规则'"
      width="640px"
    >
      <el-form ref="columnFormRef" :model="columnForm" :rules="columnFormRules" label-width="100px">
        <el-form-item v-if="!editingColumnRule" label="字段" prop="fieldId">
          <el-select v-model="columnForm.fieldId" filterable placeholder="请选择字段">
            <el-option
              v-for="field in fieldOptions"
              :key="field.id"
              :label="field.label"
              :value="field.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-else label="字段">
          <div class="readonly-value">{{ resolveFieldName(columnForm.fieldId) }}</div>
        </el-form-item>
        <el-form-item v-if="!editingColumnRule" label="目标类型" prop="targetType">
          <el-select
            v-model="columnForm.targetType"
            placeholder="请选择目标类型"
            @change="handleColumnTargetTypeChange"
          >
            <el-option
              v-for="option in targetTypeOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="!editingColumnRule" label="目标对象" prop="targetId">
          <el-select v-model="columnForm.targetId" filterable placeholder="请选择目标对象">
            <el-option
              v-for="option in currentTargetOptions"
              :key="option.id"
              :label="option.name"
              :value="option.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-else label="目标对象">
          <div class="readonly-value">
            {{ resolveTargetName(columnForm.targetType, columnForm.targetId) }}
          </div>
        </el-form-item>
        <el-form-item label="动作" prop="action">
          <el-select v-model="columnForm.action" placeholder="请选择动作">
            <el-option
              v-for="option in actionOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="启用状态" prop="enabled">
          <el-switch v-model="columnForm.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="columnDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="dialogLoading" @click="submitColumnRule"
          >保存</el-button
        >
      </template>
    </el-dialog>

    <el-dialog v-model="whitelistDialogVisible" title="新增白名单" width="560px">
      <el-form
        ref="whitelistFormRef"
        :model="whitelistForm"
        :rules="whitelistFormRules"
        label-width="100px"
      >
        <el-form-item label="用户" prop="userId">
          <el-select v-model="whitelistForm.userId" filterable placeholder="请选择用户">
            <el-option
              v-for="user in userOptions"
              :key="user.id"
              :label="user.name"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="作用范围" prop="scope">
          <el-select v-model="whitelistForm.scope" placeholder="请选择作用范围">
            <el-option
              v-for="option in whitelistScopeOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="whitelistDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="dialogLoading" @click="submitWhitelist">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import {
  createColumnPermissionApi,
  createPermissionWhitelistApi,
  createRowPermissionApi,
  deleteColumnPermissionApi,
  deletePermissionWhitelistApi,
  deleteRowPermissionApi,
  editColumnPermissionApi,
  editRowPermissionApi,
  listColumnPermissionApi,
  listPermissionWhitelistApi,
  listRowPermissionApi,
  queryRoleApi,
  queryUserOptionsApi
} from '@/api/auth'
import { getDatasetTree, listFieldByDatasetGroup } from '@/api/dataset'
import { useUserStoreWithOut } from '@/store/modules/user'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus-secondary'
import { computed, onMounted, reactive, ref } from 'vue'

interface DatasetOption {
  id: number
  name: string
}

interface TargetOption {
  id: number
  name: string
}

interface FieldOption {
  id: number
  label: string
}

interface RowRule {
  id: number
  datasetId: number
  targetType: string
  targetId: number
  filterSql: string
  enabled: boolean
  createTime?: number
  updateTime?: number
}

interface ColumnRule {
  id: number
  datasetId: number
  fieldId: number
  targetType: string
  targetId: number
  action: string
  enabled: boolean
  createTime?: number
  updateTime?: number
}

interface WhitelistEntry {
  id: number
  userId: number
  datasetId: number
  scope: string
  createTime?: number
}

const userStore = useUserStoreWithOut()

const targetTypeOptions = [
  { label: '组织', value: 'org' },
  { label: '角色', value: 'role' },
  { label: '用户', value: 'user' }
]

const actionOptions = [
  { label: '禁用', value: 'disable' },
  { label: '脱敏', value: 'desensitize' },
  { label: '掩码', value: 'mask' }
]

const whitelistScopeOptions = [
  { label: '仅行权限', value: 'row' },
  { label: '仅列权限', value: 'column' },
  { label: '行列权限', value: 'both' }
]

const targetTypeLabelMap = {
  org: '组织',
  role: '角色',
  user: '用户'
}

const actionLabelMap = {
  disable: '禁用',
  desensitize: '脱敏',
  mask: '掩码'
}

const whitelistScopeLabelMap = {
  row: '仅行权限',
  column: '仅列权限',
  both: '行列权限'
}

const pageLoading = ref(false)
const dialogLoading = ref(false)
const selectedDatasetId = ref<number>()
const datasetOptions = ref<DatasetOption[]>([])
const rowRules = ref<RowRule[]>([])
const columnRules = ref<ColumnRule[]>([])
const whitelistEntries = ref<WhitelistEntry[]>([])
const roleOptions = ref<TargetOption[]>([])
const userOptions = ref<TargetOption[]>([])
const fieldOptions = ref<FieldOption[]>([])

const rowDialogVisible = ref(false)
const columnDialogVisible = ref(false)
const whitelistDialogVisible = ref(false)
const editingRowRule = ref<RowRule | null>(null)
const editingColumnRule = ref<ColumnRule | null>(null)

const rowFormRef = ref<FormInstance>()
const columnFormRef = ref<FormInstance>()
const whitelistFormRef = ref<FormInstance>()

const rowForm = reactive({
  id: undefined as number | undefined,
  targetType: 'user',
  targetId: undefined as number | undefined,
  filterSql: '',
  enabled: true
})

const columnForm = reactive({
  id: undefined as number | undefined,
  fieldId: undefined as number | undefined,
  targetType: 'user',
  targetId: undefined as number | undefined,
  action: 'disable',
  enabled: true
})

const whitelistForm = reactive({
  userId: undefined as number | undefined,
  scope: 'both'
})

const rowFormRules: FormRules = {
  targetType: [{ required: true, message: '请选择目标类型', trigger: 'change' }],
  targetId: [{ required: true, message: '请选择目标对象', trigger: 'change' }],
  filterSql: [{ required: true, message: '请输入过滤条件', trigger: 'blur' }]
}

const columnFormRules: FormRules = {
  fieldId: [{ required: true, message: '请选择字段', trigger: 'change' }],
  targetType: [{ required: true, message: '请选择目标类型', trigger: 'change' }],
  targetId: [{ required: true, message: '请选择目标对象', trigger: 'change' }],
  action: [{ required: true, message: '请选择动作', trigger: 'change' }]
}

const whitelistFormRules: FormRules = {
  userId: [{ required: true, message: '请选择用户', trigger: 'change' }],
  scope: [{ required: true, message: '请选择作用范围', trigger: 'change' }]
}

const selectedDataset = computed(() =>
  datasetOptions.value.find(item => item.id === selectedDatasetId.value)
)

const currentTargetOptions = computed<TargetOption[]>(() => {
  if (rowDialogVisible.value) {
    return getTargetOptions(rowForm.targetType)
  }
  return getTargetOptions(columnForm.targetType)
})

const datasetWhitelist = computed(() =>
  whitelistEntries.value.filter(item => item.datasetId === selectedDatasetId.value)
)

const getTargetOptions = (targetType: string): TargetOption[] => {
  if (targetType === 'role') {
    return roleOptions.value
  }
  if (targetType === 'org') {
    const oid = Number(userStore.getOid)
    return oid ? [{ id: oid, name: `当前组织 #${oid}` }] : []
  }
  return userOptions.value
}

const flattenDatasetTree = (tree: Array<Record<string, any>>): DatasetOption[] => {
  const result: DatasetOption[] = []
  const walk = (nodes: Array<Record<string, any>>) => {
    nodes.forEach(node => {
      const children = Array.isArray(node.children) ? node.children : []
      if (node.nodeType === 'dataset' || node.leaf) {
        result.push({ id: Number(node.id), name: String(node.name || node.id) })
      }
      if (children.length) {
        walk(children)
      }
    })
  }
  walk(tree)
  return result.filter(item => !Number.isNaN(item.id))
}

const loadAllData = async () => {
  pageLoading.value = true
  try {
    const [datasetRes, roleRes, userRes, whitelistRes] = await Promise.all([
      getDatasetTree({} as any),
      queryRoleApi({}),
      queryUserOptionsApi(),
      listPermissionWhitelistApi()
    ])

    datasetOptions.value = flattenDatasetTree(
      (datasetRes as unknown as Array<Record<string, any>>) || []
    )
    roleOptions.value = (roleRes.data || []).map(item => ({ id: Number(item.id), name: item.name }))
    userOptions.value = (userRes.data || []).map(item => ({
      id: Number(item.id),
      name: item.name || item.account || `用户 #${item.id}`
    }))
    whitelistEntries.value = (whitelistRes.data || []).map(item => ({
      id: Number(item.id),
      userId: Number(item.user_id ?? item.userId),
      datasetId: Number(item.dataset_id ?? item.datasetId),
      scope: item.scope,
      createTime: item.create_time ?? item.createTime
    }))

    if (!selectedDatasetId.value && datasetOptions.value.length) {
      selectedDatasetId.value = datasetOptions.value[0].id
    }

    if (selectedDatasetId.value) {
      await loadDatasetPermissionData(selectedDatasetId.value)
    }
  } finally {
    pageLoading.value = false
  }
}

const loadDatasetPermissionData = async (datasetId: number) => {
  const [rowRes, columnRes, fieldRes] = await Promise.all([
    listRowPermissionApi({ datasetId }),
    listColumnPermissionApi({ datasetId }),
    listFieldByDatasetGroup(datasetId)
  ])

  rowRules.value = (rowRes.data || []).map(item => ({
    id: Number(item.id),
    datasetId: Number(item.dataset_id ?? item.datasetId),
    targetType: item.target_type ?? item.targetType,
    targetId: Number(item.target_id ?? item.targetId),
    filterSql: item.filter_sql ?? item.filterSql,
    enabled: Boolean(item.enabled),
    createTime: item.create_time ?? item.createTime,
    updateTime: item.update_time ?? item.updateTime
  }))

  columnRules.value = (columnRes.data || []).map(item => ({
    id: Number(item.id),
    datasetId: Number(item.dataset_id ?? item.datasetId),
    fieldId: Number(item.field_id ?? item.fieldId),
    targetType: item.target_type ?? item.targetType,
    targetId: Number(item.target_id ?? item.targetId),
    action: item.action,
    enabled: Boolean(item.enabled),
    createTime: item.create_time ?? item.createTime,
    updateTime: item.update_time ?? item.updateTime
  }))

  fieldOptions.value = ((fieldRes?.data || []) as Array<Record<string, any>>).map(field => ({
    id: Number(field.id),
    label: String(
      field.dataeaseName ||
        field.dataease_name ||
        field.name ||
        field.originName ||
        field.origin_name
    )
  }))
}

const handleDatasetChange = async (datasetId: number) => {
  if (!datasetId) {
    rowRules.value = []
    columnRules.value = []
    fieldOptions.value = []
    return
  }
  pageLoading.value = true
  try {
    await loadDatasetPermissionData(datasetId)
  } finally {
    pageLoading.value = false
  }
}

const openCreateRowDialog = () => {
  editingRowRule.value = null
  rowForm.id = undefined
  rowForm.targetType = 'user'
  rowForm.targetId = undefined
  rowForm.filterSql = ''
  rowForm.enabled = true
  rowDialogVisible.value = true
}

const openEditRowDialog = (rule: RowRule) => {
  editingRowRule.value = rule
  rowForm.id = rule.id
  rowForm.targetType = rule.targetType
  rowForm.targetId = rule.targetId
  rowForm.filterSql = rule.filterSql
  rowForm.enabled = rule.enabled
  rowDialogVisible.value = true
}

const openCreateColumnDialog = () => {
  editingColumnRule.value = null
  columnForm.id = undefined
  columnForm.fieldId = undefined
  columnForm.targetType = 'user'
  columnForm.targetId = undefined
  columnForm.action = 'disable'
  columnForm.enabled = true
  columnDialogVisible.value = true
}

const openEditColumnDialog = (rule: ColumnRule) => {
  editingColumnRule.value = rule
  columnForm.id = rule.id
  columnForm.fieldId = rule.fieldId
  columnForm.targetType = rule.targetType
  columnForm.targetId = rule.targetId
  columnForm.action = rule.action
  columnForm.enabled = rule.enabled
  columnDialogVisible.value = true
}

const openCreateWhitelistDialog = () => {
  whitelistForm.userId = undefined
  whitelistForm.scope = 'both'
  whitelistDialogVisible.value = true
}

const handleRowTargetTypeChange = () => {
  rowForm.targetId = undefined
}

const handleColumnTargetTypeChange = () => {
  columnForm.targetId = undefined
}

const submitRowRule = async () => {
  if (!selectedDatasetId.value) return
  await rowFormRef.value?.validate()
  dialogLoading.value = true
  try {
    if (editingRowRule.value && rowForm.id) {
      await editRowPermissionApi({
        id: rowForm.id,
        filterSql: rowForm.filterSql.trim(),
        enabled: rowForm.enabled
      })
      ElMessage.success('行权限规则更新成功')
    } else {
      await createRowPermissionApi({
        datasetId: selectedDatasetId.value,
        targetType: rowForm.targetType,
        targetId: Number(rowForm.targetId),
        filterSql: rowForm.filterSql.trim(),
        enabled: rowForm.enabled
      })
      ElMessage.success('行权限规则创建成功')
    }
    rowDialogVisible.value = false
    await loadDatasetPermissionData(selectedDatasetId.value)
  } finally {
    dialogLoading.value = false
  }
}

const submitColumnRule = async () => {
  if (!selectedDatasetId.value) return
  await columnFormRef.value?.validate()
  dialogLoading.value = true
  try {
    if (editingColumnRule.value && columnForm.id) {
      await editColumnPermissionApi({
        id: columnForm.id,
        action: columnForm.action,
        enabled: columnForm.enabled
      })
      ElMessage.success('列权限规则更新成功')
    } else {
      await createColumnPermissionApi({
        datasetId: selectedDatasetId.value,
        fieldId: Number(columnForm.fieldId),
        targetType: columnForm.targetType,
        targetId: Number(columnForm.targetId),
        action: columnForm.action,
        enabled: columnForm.enabled
      })
      ElMessage.success('列权限规则创建成功')
    }
    columnDialogVisible.value = false
    await loadDatasetPermissionData(selectedDatasetId.value)
  } finally {
    dialogLoading.value = false
  }
}

const submitWhitelist = async () => {
  if (!selectedDatasetId.value) return
  await whitelistFormRef.value?.validate()
  dialogLoading.value = true
  try {
    await createPermissionWhitelistApi({
      userId: Number(whitelistForm.userId),
      datasetId: selectedDatasetId.value,
      scope: whitelistForm.scope
    })
    whitelistDialogVisible.value = false
    ElMessage.success('白名单保存成功')
    const whitelistRes = await listPermissionWhitelistApi()
    whitelistEntries.value = (whitelistRes.data || []).map(item => ({
      id: Number(item.id),
      userId: Number(item.user_id ?? item.userId),
      datasetId: Number(item.dataset_id ?? item.datasetId),
      scope: item.scope,
      createTime: item.create_time ?? item.createTime
    }))
  } finally {
    dialogLoading.value = false
  }
}

const handleToggleRowRule = async (rule: RowRule, enabled: boolean) => {
  await editRowPermissionApi({ id: rule.id, enabled })
  rule.enabled = enabled
  ElMessage.success('行权限状态已更新')
}

const handleToggleColumnRule = async (rule: ColumnRule, enabled: boolean) => {
  await editColumnPermissionApi({ id: rule.id, enabled })
  rule.enabled = enabled
  ElMessage.success('列权限状态已更新')
}

const handleDeleteRowRule = async (rule: RowRule) => {
  await ElMessageBox.confirm(
    `确认删除行权限规则「${resolveTargetName(rule.targetType, rule.targetId)}」吗？`,
    '提示',
    {
      type: 'warning'
    }
  )
  await deleteRowPermissionApi(rule.id)
  rowRules.value = rowRules.value.filter(item => item.id !== rule.id)
  ElMessage.success('行权限规则已删除')
}

const handleDeleteColumnRule = async (rule: ColumnRule) => {
  await ElMessageBox.confirm(
    `确认删除列权限规则「${resolveFieldName(rule.fieldId)}」吗？`,
    '提示',
    {
      type: 'warning'
    }
  )
  await deleteColumnPermissionApi(rule.id)
  columnRules.value = columnRules.value.filter(item => item.id !== rule.id)
  ElMessage.success('列权限规则已删除')
}

const handleDeleteWhitelist = async (entry: WhitelistEntry) => {
  await ElMessageBox.confirm(`确认移除白名单用户「${resolveUserName(entry.userId)}」吗？`, '提示', {
    type: 'warning'
  })
  await deletePermissionWhitelistApi(entry.id)
  whitelistEntries.value = whitelistEntries.value.filter(item => item.id !== entry.id)
  ElMessage.success('白名单已删除')
}

const resolveTargetName = (targetType: string, targetId: number) => {
  const option = getTargetOptions(targetType).find(item => item.id === Number(targetId))
  if (option) {
    return option.name
  }
  if (targetType === 'org') {
    return `组织 #${targetId}`
  }
  if (targetType === 'role') {
    return `角色 #${targetId}`
  }
  return `用户 #${targetId}`
}

const resolveFieldName = (fieldId: number) => {
  return fieldOptions.value.find(item => item.id === Number(fieldId))?.label || `字段 #${fieldId}`
}

const resolveUserName = (userId: number) => {
  return userOptions.value.find(item => item.id === Number(userId))?.name || `用户 #${userId}`
}

const formatTimestamp = (value?: number) => {
  if (!value) return '-'
  const date = new Date(Number(value))
  if (Number.isNaN(date.getTime())) return String(value)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(
    date.getDate()
  ).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(
    date.getMinutes()
  ).padStart(2, '0')}:${String(date.getSeconds()).padStart(2, '0')}`
}

onMounted(async () => {
  await loadAllData()
})
</script>

<style scoped lang="less">
.row-column-permission-page {
  .page-header,
  .section-header,
  .filter-grid {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
  }

  .page-header,
  .filter-card,
  .section-card {
    padding: 16px;
    margin-bottom: 16px;
    background: var(--ContentBG, #fff);
    border: 1px solid #ebedf0;
    border-radius: 12px;
  }

  .page-header h3,
  .section-header h4 {
    margin: 0;
    color: #1f2329;
  }

  .page-header p,
  .section-header p {
    margin: 6px 0 0;
    color: #646a73;
    line-height: 20px;
  }

  .filter-grid {
    align-items: end;
    flex-wrap: wrap;
  }

  .filter-item {
    min-width: 240px;
    flex: 1;
  }

  .filter-label {
    display: block;
    margin-bottom: 8px;
    color: #646a73;
    font-size: 13px;
  }

  .current-dataset-name,
  .readonly-value {
    min-height: 32px;
    padding: 6px 10px;
    color: #1f2329;
    background: #f5f7fa;
    border-radius: 8px;
    line-height: 20px;
  }

  .section-header {
    margin-bottom: 16px;
  }
}
</style>
