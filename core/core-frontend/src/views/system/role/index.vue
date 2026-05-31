<template>
  <div class="role-management-page">
    <div class="page-header">
      <p class="router-title">角色管理</p>
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
        <el-button type="primary" @click="openCreateDialog">新增角色</el-button>
      </div>
    </div>

    <div class="page-body page-layout" v-loading="loading">
      <aside class="tree-sidebar role-sidebar" role="complementary">
        <div class="sidebar-caption">角色列表</div>
        <div class="sidebar-table-wrap">
          <el-table
            class="role-table"
            :data="roles"
            border
            row-key="id"
            highlight-current-row
            :current-row-key="currentRole?.id"
            height="100%"
            @current-change="handleRoleSelect"
          >
            <el-table-column prop="name" label="角色名称" min-width="124" show-overflow-tooltip />
            <el-table-column label="类型" width="104">
              <template #default="scope">
                <el-tag :type="scope.row.type === 0 ? 'info' : 'success'">
                  {{ scope.row.type === 0 ? '内置' : '自定义' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="memberCount" label="成员数" width="76" />
          </el-table>
        </div>
      </aside>

      <section class="table-panel" aria-label="角色成员管理">
        <template v-if="currentRole">
          <div class="table-panel-header">
            <div class="panel-copy">
              <div class="panel-title-row">
                <h3>{{ currentRole.name }}</h3>
                <el-tag :type="currentRole.type === 0 ? 'info' : 'success'">
                  {{ currentRole.type === 0 ? '内置角色' : '自定义角色' }}
                </el-tag>
                <div class="selected-summary">成员 {{ currentRole.memberCount }}</div>
              </div>
              <p>{{ currentRole.description || '当前角色暂无描述，可通过编辑角色补充说明。' }}</p>
            </div>
            <div class="panel-header-actions">
              <el-button :disabled="currentRole.type === 0" @click="openEditDialog(currentRole)">
                编辑角色
              </el-button>
              <el-button
                type="danger"
                plain
                :disabled="currentRole.type === 0"
                @click="handleDelete(currentRole)"
              >
                删除角色
              </el-button>
              <el-button @click="openMemberDialog">挂载组织内用户</el-button>
              <el-button @click="openExternalDialog">挂载外部用户</el-button>
              <el-button :disabled="selectedMemberIds.length === 0" @click="handleBatchUnMountUser">
                批量卸载
              </el-button>
            </div>
          </div>

          <div class="table-panel-body">
            <div class="table-wrap">
              <el-table
                :data="members"
                border
                height="100%"
                @selection-change="handleMemberSelectionChange"
              >
                <el-table-column type="selection" width="48" />
                <el-table-column prop="account" label="账号" min-width="140" />
                <el-table-column prop="name" label="姓名" min-width="120" />
                <el-table-column prop="email" label="邮箱" min-width="180" />
                <el-table-column prop="phone" label="手机号" min-width="140" />
                <el-table-column label="状态" width="100">
                  <template #default="scope">
                    {{ scope.row.enable ? '启用' : '停用' }}
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="100" fixed="right">
                  <template #default="scope">
                    <el-button link type="danger" @click="handleUnMountUser(scope.row)"
                      >卸载</el-button
                    >
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <div class="pagination-wrap">
              <el-pagination
                v-model:current-page="memberPage"
                v-model:page-size="memberPageSize"
                background
                layout="total, prev, pager, next, sizes"
                :page-sizes="[10, 20, 50, 100]"
                :total="memberTotal"
                @current-change="loadMembers"
                @size-change="handleMemberSizeChange"
              />
            </div>
          </div>
        </template>
        <div v-else class="empty-panel">
          <el-empty description="请选择角色查看成员详情" />
        </div>
      </section>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新增角色' : '编辑角色'"
      width="520px"
      append-to-body
      :before-close="closeDialog"
    >
      <el-form ref="formRef" :model="form" :rules="formRules" label-position="top">
        <el-form-item v-if="dialogMode === 'create'" label="继承内置角色" prop="inheritRoleId">
          <el-select v-model="form.inheritRoleId" placeholder="请选择内置角色" style="width: 100%">
            <el-option
              v-for="role in builtinRoleOptions"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" maxlength="255" />
        </el-form-item>
        <el-form-item label="角色描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="4"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <div v-if="dialogMode === 'create'" class="dialog-tip">
        当前仅记录继承来源，权限配置将在后续权限中心中完善。
      </div>
      <template #footer>
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="memberDialogVisible" title="挂载组织内用户" width="600px" append-to-body>
      <div class="member-dialog-toolbar">
        <el-input
          v-model="memberKeyword"
          clearable
          placeholder="搜索账号/姓名"
          style="width: 220px"
          @keyup.enter="loadMountableUsers"
        />
        <el-button @click="loadMountableUsers">搜索</el-button>
      </div>
      <el-select
        v-model="selectedMountUserIds"
        multiple
        collapse-tags
        collapse-tags-tooltip
        placeholder="选择要挂载的用户"
        style="width: 100%"
      >
        <el-option
          v-for="item in mountableUsers"
          :key="item.id"
          :label="`${item.name}（${item.account}）`"
          :value="item.id"
        />
      </el-select>
      <template #footer>
        <el-button @click="memberDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="!selectedMountUserIds.length"
          @click="handleMountUsers"
        >
          挂载用户
        </el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="externalDialogVisible" title="挂载外部用户" width="600px" append-to-body>
      <div class="member-dialog-toolbar">
        <el-input
          v-model="externalKeyword"
          clearable
          placeholder="搜索账号/姓名"
          style="width: 220px"
          @keyup.enter="loadExternalUsers"
        />
        <el-button @click="loadExternalUsers">搜索</el-button>
      </div>
      <el-select
        v-model="selectedExternalAccounts"
        multiple
        collapse-tags
        collapse-tags-tooltip
        placeholder="选择要挂载的外部用户"
        style="width: 100%"
      >
        <el-option
          v-for="item in externalUsers"
          :key="item.id"
          :label="`${item.name}（${item.account}）`"
          :value="item.account"
        />
      </el-select>
      <template #footer>
        <el-button @click="externalDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="!selectedExternalAccounts.length"
          @click="handleMountExternalUsers"
        >
          挂载外部用户
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus-secondary'
import { ElMessage, ElMessageBox } from 'element-plus-secondary'
import {
  beforeUnmountInfoApi,
  mountExternalUserApi,
  mountUserApi,
  roleCreateApi,
  roleDelApi,
  roleEditApi,
  searchExternalUserApi,
  searchRoleApi,
  unMountUserApi,
  userOptionForRoleApi,
  userSelectedForRoleApi
} from '@/api/user'

interface RoleItem {
  id: number
  name: string
  description?: string
  type: number
  memberCount: number
}

interface UserOption {
  id: number
  account: string
  name: string
  email?: string
  phone?: string
  enable: boolean
}

const loading = ref(false)
const keyword = ref('')
const roles = ref<RoleItem[]>([])
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const memberDialogVisible = ref(false)
const externalDialogVisible = ref(false)
const members = ref<UserOption[]>([])
const mountableUsers = ref<UserOption[]>([])
const externalUsers = ref<UserOption[]>([])
const selectedMountUserIds = ref<number[]>([])
const selectedExternalAccounts = ref<string[]>([])
const selectedMemberIds = ref<number[]>([])
const memberKeyword = ref('')
const externalKeyword = ref('')
const currentRole = ref<RoleItem | null>(null)
const formRef = ref<FormInstance>()
const memberPage = ref(1)
const memberPageSize = ref(10)
const memberTotal = ref(0)

const form = reactive({
  id: undefined as number | undefined,
  name: '',
  description: '',
  inheritRoleId: undefined as number | undefined
})

const formRules: FormRules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  inheritRoleId: [{ required: true, message: '请选择内置角色', trigger: 'change' }]
}

const builtinRoleOptions = computed(() => roles.value.filter(role => role.type === 0))

const loadRoles = async () => {
  loading.value = true
  try {
    const res = await searchRoleApi(keyword.value.trim())
    roles.value = (res.data || []).map(role => ({
      ...role,
      memberCount: role.memberCount || 0
    }))
    if (currentRole.value) {
      currentRole.value = roles.value.find(role => role.id === currentRole.value?.id) || null
    }
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  form.id = undefined
  form.name = ''
  form.description = ''
  form.inheritRoleId = undefined
}

const closeDialog = () => {
  formRef.value?.clearValidate()
  dialogVisible.value = false
  resetForm()
}

const openCreateDialog = () => {
  dialogMode.value = 'create'
  resetForm()
  dialogVisible.value = true
}

const openEditDialog = (row: RoleItem) => {
  if (row.type === 0) {
    ElMessage.warning('内置角色不允许编辑')
    return
  }
  dialogMode.value = 'edit'
  form.id = row.id
  form.name = row.name
  form.description = row.description || ''
  dialogVisible.value = true
}

const submitForm = async () => {
  await formRef.value?.validate()
  const payload = {
    name: form.name.trim(),
    description: form.description.trim() || undefined
  }
  if (dialogMode.value === 'create') {
    await roleCreateApi(payload)
    ElMessage.success('新增成功')
  } else if (form.id) {
    await roleEditApi({ id: form.id, ...payload })
    ElMessage.success('编辑成功')
  }
  closeDialog()
  await loadRoles()
}

const handleDelete = async (row: RoleItem) => {
  if (row.type === 0) {
    ElMessage.warning('内置角色不允许删除')
    return
  }
  await ElMessageBox.confirm(`确认删除角色“${row.name}”吗？`, '删除角色', {
    type: 'warning',
    confirmButtonType: 'danger',
    autofocus: false,
    showClose: false
  })
  await roleDelApi(row.id)
  ElMessage.success('删除成功')
  if (currentRole.value?.id === row.id) {
    currentRole.value = null
    members.value = []
    memberTotal.value = 0
  }
  await loadRoles()
}

const loadMembers = async () => {
  if (!currentRole.value) {
    return
  }
  const res = await userSelectedForRoleApi(memberPage.value, memberPageSize.value, {
    roleId: currentRole.value.id
  })
  members.value = res.data?.items || []
  memberTotal.value = res.data?.total || 0
}

const handleRoleSelect = async (row: RoleItem | undefined) => {
  if (!row) {
    return
  }
  currentRole.value = row
  selectedMemberIds.value = []
  memberPage.value = 1
  await loadMembers()
}

const handleMemberSizeChange = async (size: number) => {
  memberPageSize.value = size
  memberPage.value = 1
  await loadMembers()
}

const handleMemberSelectionChange = (rows: UserOption[]) => {
  selectedMemberIds.value = rows.map(item => item.id)
}

const loadMountableUsers = async () => {
  const res = await userOptionForRoleApi({ keyword: memberKeyword.value.trim() || undefined })
  const memberIds = new Set(members.value.map(item => item.id))
  mountableUsers.value = (res.data || []).filter(item => !memberIds.has(item.id))
}

const openMemberDialog = async () => {
  if (!currentRole.value) {
    ElMessage.warning('请先选择角色')
    return
  }
  selectedMountUserIds.value = []
  memberKeyword.value = ''
  memberDialogVisible.value = true
  await loadMountableUsers()
}

const handleMountUsers = async () => {
  if (!currentRole.value || !selectedMountUserIds.value.length) {
    return
  }
  await mountUserApi({ roleId: currentRole.value.id, userIds: selectedMountUserIds.value })
  ElMessage.success('挂载成功')
  memberDialogVisible.value = false
  await loadMembers()
  await loadRoles()
}

const loadExternalUsers = async () => {
  if (!externalKeyword.value.trim()) {
    externalUsers.value = []
    return
  }
  const res = await searchExternalUserApi(externalKeyword.value.trim())
  externalUsers.value = res.data || []
}

const openExternalDialog = () => {
  if (!currentRole.value) {
    ElMessage.warning('请先选择角色')
    return
  }
  selectedExternalAccounts.value = []
  externalKeyword.value = ''
  externalUsers.value = []
  externalDialogVisible.value = true
}

const handleMountExternalUsers = async () => {
  if (!currentRole.value || !selectedExternalAccounts.value.length) {
    return
  }
  const res = await mountExternalUserApi({
    roleId: currentRole.value.id,
    accounts: selectedExternalAccounts.value
  })
  const notFound = res.data?.notFound || []
  if (notFound.length) {
    ElMessage.warning(`以下账号未找到：${notFound.join('、')}`)
  } else {
    ElMessage.success('挂载成功')
  }
  externalDialogVisible.value = false
  await loadMembers()
  await loadRoles()
}

const handleUnMountUser = async (row: UserOption) => {
  if (!currentRole.value) {
    return
  }
  const infoRes = await beforeUnmountInfoApi({ roleId: currentRole.value.id, userIds: [row.id] })
  const remainingRoleCount = infoRes.data?.[0]?.remainingRoleCount
  const message =
    remainingRoleCount === 0
      ? `卸载后用户“${row.name}”将失去所有角色并被系统删除，确认继续吗？`
      : `确认从角色“${currentRole.value.name}”中卸载用户“${row.name}”吗？`
  await ElMessageBox.confirm(message, '卸载成员', {
    type: 'warning',
    confirmButtonType: 'danger',
    autofocus: false,
    showClose: false
  })
  await unMountUserApi({ roleId: currentRole.value.id, userIds: [row.id] })
  ElMessage.success('卸载成功')
  await loadMembers()
  await loadRoles()
}

const handleBatchUnMountUser = async () => {
  if (!currentRole.value || !selectedMemberIds.value.length) {
    return
  }
  const infoRes = await beforeUnmountInfoApi({
    roleId: currentRole.value.id,
    userIds: selectedMemberIds.value
  })
  const zeroCountUsers = (infoRes.data || []).filter(item => item.remainingRoleCount === 0)
  const message = zeroCountUsers.length
    ? `以下用户卸载后将失去所有角色并被系统删除：${zeroCountUsers
        .map(item => item.name || item.account)
        .join('、')}`
    : `确认批量卸载选中的 ${selectedMemberIds.value.length} 个用户吗？`
  await ElMessageBox.confirm(message, '批量卸载成员', {
    type: 'warning',
    confirmButtonType: 'danger',
    autofocus: false,
    showClose: false
  })
  await unMountUserApi({ roleId: currentRole.value.id, userIds: selectedMemberIds.value })
  ElMessage.success('批量卸载成功')
  selectedMemberIds.value = []
  await loadMembers()
  await loadRoles()
}

onMounted(() => {
  loadRoles()
})
</script>

<style scoped lang="less">
.role-management-page {
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

  .toolbar,
  .member-dialog-toolbar {
    display: flex;
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
  }

  .page-body {
    background: var(--ContentBG, #ffffff);
    border-radius: 12px;
  }

  .page-layout {
    display: grid;
    grid-template-columns: 380px minmax(0, 1fr);
    min-height: calc(100vh - 176px);
    padding: 0;
    overflow: hidden;
  }

  .tree-sidebar {
    padding: 16px 12px 16px 16px;
    background: var(--ContentBG, #ffffff);
    border-right: 1px solid #ebedf0;
    overflow-y: auto;
  }

  .role-sidebar {
    display: flex;
    flex-direction: column;
    min-width: 0;
    overflow-y: auto;
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

  .table-panel-body {
    display: flex;
    flex: 1;
    flex-direction: column;
    min-height: 0;
    gap: 16px;
  }

  .table-wrap {
    flex: 1;
    min-height: 0;
  }

  .pagination-wrap {
    display: flex;
    justify-content: flex-end;
  }

  .empty-panel {
    display: flex;
    flex: 1;
    align-items: center;
    justify-content: center;
  }

  .dialog-tip {
    margin-top: -4px;
    color: #646a73;
    font-size: 13px;
  }

  .member-dialog-toolbar {
    margin-bottom: 12px;
  }

  :deep(.role-table .el-table__row.current-row > td.el-table__cell) {
    background: rgba(51, 112, 255, 0.08);
  }

  :deep(.role-table .el-table__body tr:hover > td.el-table__cell) {
    background: rgba(51, 112, 255, 0.04);
  }

  :deep(.role-table .el-table__body td.el-table__cell) {
    padding-top: 10px;
    padding-bottom: 10px;
  }
}
</style>
