<template>
  <div class="user-management-page" v-loading="loading">
    <div class="page-header">
      <p class="router-title">用户管理</p>
      <div class="toolbar">
        <el-input
          v-model="keyword"
          clearable
          placeholder="搜索账号/姓名/邮箱/手机号"
          style="width: 240px"
          @keyup.enter="handleSearch"
        />
        <el-select v-model="enableFilter" clearable placeholder="状态" style="width: 100px">
          <el-option label="启用" :value="true" />
          <el-option label="停用" :value="false" />
        </el-select>
        <el-select v-model="orgFilter" clearable placeholder="所属组织" style="width: 160px">
          <el-option
            v-for="item in orgFlatList"
            :key="item.id"
            :label="item.label"
            :value="item.id"
          />
        </el-select>
        <el-button @click="handleSearch">查询</el-button>
        <el-button type="primary" @click="openCreateDialog">新增用户</el-button>
        <el-button :disabled="selectedIds.length === 0" @click="handleBatchDelete"
          >批量删除</el-button
        >
      </div>
    </div>

    <div class="page-body">
      <el-table :data="users" border @selection-change="handleSelectionChange">
        <el-table-column type="selection" width="48" />
        <el-table-column prop="account" label="账号" min-width="140" />
        <el-table-column prop="name" label="姓名" min-width="120" />
        <el-table-column prop="email" label="邮箱" min-width="180" show-overflow-tooltip />
        <el-table-column prop="phone" label="手机号" min-width="140" />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-switch
              :model-value="scope.row.enable"
              inline-prompt
              active-text="启用"
              inactive-text="停用"
              @change="value => handleToggleEnable(scope.row, value)"
            />
          </template>
        </el-table-column>
        <el-table-column label="角色" min-width="220" show-overflow-tooltip>
          <template #default="scope">
            <span>{{ formatRoleNames(scope.row.roleIds) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="所属组织" min-width="140">
          <template #default="scope">
            <span>{{ scope.row.orgName || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="260">
          <template #default="scope">
            <el-button link type="primary" @click="openEditDialog(scope.row)">编辑</el-button>
            <el-button link type="warning" @click="handleResetPassword(scope.row)"
              >重置密码</el-button
            >
            <el-button link type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-wrap">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          background
          layout="total, prev, pager, next, sizes"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          @current-change="loadUsers"
          @size-change="handleSizeChange"
        />
      </div>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '新增用户' : '编辑用户'"
      width="560px"
      append-to-body
      :before-close="closeDialog"
    >
      <el-form ref="formRef" :model="form" :rules="formRules" label-position="top">
        <el-form-item label="账号" prop="account">
          <el-input v-model="form.account" :disabled="dialogMode === 'edit'" maxlength="255" />
        </el-form-item>
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" maxlength="255" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" maxlength="255" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" maxlength="255" />
        </el-form-item>
        <el-form-item v-if="dialogMode === 'create'" label="所属组织" prop="oid">
          <el-select v-model="form.oid" placeholder="请选择组织" style="width: 100%">
            <el-option
              v-for="item in orgFlatList"
              :key="item.id"
              :label="item.label"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item v-if="dialogMode === 'create'" label="是否启用">
          <el-switch v-model="form.enable" inline-prompt active-text="启用" inactive-text="停用" />
        </el-form-item>
        <el-form-item label="角色" prop="roleIds">
          <el-select
            v-model="form.roleIds"
            multiple
            collapse-tags
            collapse-tags-tooltip
            style="width: 100%"
          >
            <el-option
              v-for="role in roleOptions"
              :key="role.id"
              :label="role.name"
              :value="role.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <div v-if="dialogMode === 'create'" class="dialog-tip">
        默认密码：{{ defaultPassword || '加载中...' }}
      </div>
      <template #footer>
        <el-button @click="closeDialog">取消</el-button>
        <el-button type="primary" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script lang="ts" setup>
import { computed, onMounted, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus-secondary'
import { ElMessage, ElMessageBox } from 'element-plus-secondary'
import {
  batchDelApi,
  defaultPwdApi,
  queryFormApi,
  resetPwdApi,
  searchRoleApi,
  switchEnableApi,
  userCreateApi,
  userDelApi,
  userEditApi,
  userPageApi
} from '@/api/user'
import { searchApi as orgSearchApi } from '@/api/org'

interface RoleOption {
  id: number
  name: string
}

interface UserItem {
  id: number
  account: string
  name: string
  email?: string
  phone?: string
  enable: boolean
  roleIds: number[]
  oid?: number
  orgName?: string
}

interface OrgTreeNode {
  id: string
  name: string
  children?: OrgTreeNode[]
}

interface OrgFlatItem {
  id: number
  label: string
}

const loading = ref(false)
const keyword = ref('')
const enableFilter = ref<boolean | undefined>()
const orgFilter = ref<number | undefined>()
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)
const users = ref<UserItem[]>([])
const roleOptions = ref<RoleOption[]>([])
const selectedIds = ref<number[]>([])
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const formRef = ref<FormInstance>()
const defaultPassword = ref('')
const orgNameMap = ref<Record<number, string>>({})
const orgTreeData = ref<OrgTreeNode[]>([])

const form = reactive({
  id: undefined as number | undefined,
  account: '',
  name: '',
  email: '',
  phone: '',
  roleIds: [] as number[],
  oid: undefined as number | undefined,
  enable: true
})

const formRules: FormRules = {
  account: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  roleIds: [{ type: 'array', required: true, message: '请至少选择一个角色', trigger: 'change' }],
  oid: [{ required: true, message: '请选择组织', trigger: 'change' }]
}

const orgFlatList = computed<OrgFlatItem[]>(() => {
  const items: OrgFlatItem[] = []
  const walk = (nodes: OrgTreeNode[], prefix = '') => {
    nodes.forEach(node => {
      const nodeId = Number(node.id)
      if (!Number.isNaN(nodeId) && nodeId !== 0) {
        items.push({ id: nodeId, label: `${prefix}${node.name}` })
      }
      if (node.children?.length) {
        walk(node.children, `${prefix}${node.name} / `)
      }
    })
  }
  walk(orgTreeData.value)
  return items
})

const buildOrgNameMap = (nodes: OrgTreeNode[]) => {
  const map: Record<number, string> = {}
  const walk = (items: OrgTreeNode[]) => {
    items.forEach(node => {
      const nodeId = Number(node.id)
      if (!Number.isNaN(nodeId) && nodeId !== 0) {
        map[nodeId] = node.name
      }
      if (node.children?.length) {
        walk(node.children)
      }
    })
  }
  walk(nodes)
  orgNameMap.value = map
}

const loadOrgMap = async () => {
  const res = await orgSearchApi({})
  orgTreeData.value = res.data || []
  buildOrgNameMap(orgTreeData.value)
}

const loadRoleOptions = async () => {
  const res = await searchRoleApi('')
  roleOptions.value = res.data || []
}

const loadDefaultPassword = async () => {
  const res = await defaultPwdApi()
  defaultPassword.value = res.data?.password || ''
}

const loadUsers = async () => {
  loading.value = true
  try {
    const res = await userPageApi(page.value, pageSize.value, {
      keyword: keyword.value.trim() || undefined,
      enable: enableFilter.value,
      oid: orgFilter.value
    })
    users.value = (res.data?.items || []).map(item => ({
      ...item,
      orgName: item.oid ? orgNameMap.value[item.oid] || item.orgName || '-' : '-'
    }))
    total.value = res.data?.total || 0
  } finally {
    loading.value = false
  }
}

const handleSearch = async () => {
  page.value = 1
  await loadUsers()
}

const handleSizeChange = async (size: number) => {
  pageSize.value = size
  page.value = 1
  await loadUsers()
}

const handleSelectionChange = (rows: UserItem[]) => {
  selectedIds.value = rows.map(item => item.id)
}

const resetForm = () => {
  form.id = undefined
  form.account = ''
  form.name = ''
  form.email = ''
  form.phone = ''
  form.roleIds = []
  form.oid = undefined
  form.enable = true
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

const openEditDialog = async (row: UserItem) => {
  dialogMode.value = 'edit'
  const res = await queryFormApi(row.id)
  const detail = res.data
  form.id = detail.id
  form.account = detail.account || ''
  form.name = detail.name || ''
  form.email = detail.email || ''
  form.phone = detail.phone || ''
  form.roleIds = detail.roleIds || []
  dialogVisible.value = true
}

const submitForm = async () => {
  await formRef.value?.validate()
  if (dialogMode.value === 'create') {
    const payload = {
      account: form.account.trim(),
      name: form.name.trim(),
      email: form.email.trim() || undefined,
      phone: form.phone.trim() || undefined,
      roleIds: form.roleIds,
      oid: form.oid
    }
    await userCreateApi(payload)
    ElMessage.success('新增成功')
  } else if (form.id) {
    const payload = {
      account: form.account.trim(),
      name: form.name.trim(),
      email: form.email.trim() || undefined,
      phone: form.phone.trim() || undefined,
      roleIds: form.roleIds,
      id: form.id
    }
    await userEditApi(payload)
    ElMessage.success('编辑成功')
  }
  closeDialog()
  await loadUsers()
}

const handleDelete = async (row: UserItem) => {
  await ElMessageBox.confirm(`确认删除用户"${row.name}"吗？`, '删除用户', {
    type: 'warning',
    confirmButtonType: 'danger',
    autofocus: false,
    showClose: false
  })
  await userDelApi(row.id)
  ElMessage.success('删除成功')
  await loadUsers()
}

const handleBatchDelete = async () => {
  await ElMessageBox.confirm(
    `确认批量删除选中的 ${selectedIds.value.length} 个用户吗？`,
    '批量删除用户',
    {
      type: 'warning',
      confirmButtonType: 'danger',
      autofocus: false,
      showClose: false
    }
  )
  await batchDelApi({ ids: selectedIds.value })
  ElMessage.success('批量删除成功')
  selectedIds.value = []
  await loadUsers()
}

const handleResetPassword = async (row: UserItem) => {
  await ElMessageBox.confirm(`确认重置用户"${row.name}"的密码吗？`, '重置密码', {
    type: 'warning',
    autofocus: false,
    showClose: false
  })
  await resetPwdApi(row.id)
  ElMessage.success(`重置成功，默认密码为：${defaultPassword.value || '系统默认密码'}`)
}

const handleToggleEnable = async (row: UserItem, value: boolean | string | number) => {
  const enable = Boolean(value)
  await switchEnableApi({ id: row.id, enable })
  ElMessage.success(enable ? '已启用' : '已停用')
  row.enable = enable
}

const formatRoleNames = (roleIds: number[]) => {
  if (!roleIds?.length) {
    return '-'
  }
  const nameMap = new Map(roleOptions.value.map(item => [item.id, item.name]))
  return roleIds.map(id => nameMap.get(id) || `角色#${id}`).join('、')
}

onMounted(async () => {
  await Promise.all([loadRoleOptions(), loadOrgMap(), loadDefaultPassword()])
  await loadUsers()
})
</script>

<style scoped lang="less">
.user-management-page {
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
    font-size: 20px;
    font-weight: 500;
    line-height: 28px;
  }

  .toolbar {
    display: flex;
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
    justify-content: flex-end;
  }

  .page-body {
    padding: 16px;
    background: var(--ContentBG, #ffffff);
    border-radius: 12px;
  }

  .pagination-wrap {
    display: flex;
    justify-content: flex-end;
    margin-top: 16px;
  }

  .dialog-tip {
    margin-top: -4px;
    color: #646a73;
    font-size: 13px;
  }
}
</style>
