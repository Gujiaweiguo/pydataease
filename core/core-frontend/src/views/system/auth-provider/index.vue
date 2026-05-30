<template>
  <div class="auth-provider-page" v-loading="loading">
    <div class="page-header">
      <p class="router-title">{{ t('auth_provider.title') }}</p>
      <div class="toolbar">
        <el-button type="primary" @click="openCreateDialog">
          {{ t('auth_provider.create') }}
        </el-button>
      </div>
    </div>

    <div class="page-body">
      <el-table :data="providers" border>
        <el-table-column prop="name" :label="t('auth_provider.name')" min-width="160" />
        <el-table-column prop="type" :label="t('auth_provider.type')" width="120">
          <template #default="{ row }">
            <el-tag>{{ t(`auth_provider.type_${row.type}`) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('auth_provider.status')" width="100">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" @change="() => handleToggle(row)" />
          </template>
        </el-table-column>
        <el-table-column :label="t('auth_provider.is_default')" width="120">
          <template #default="{ row }">
            <el-tag v-if="row.isDefault" type="success">{{ t('auth_provider.is_default') }}</el-tag>
            <el-button v-else link type="primary" @click="handleSetDefault(row)">
              {{ t('auth_provider.set_default') }}
            </el-button>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.create_time')" min-width="160">
          <template #default="{ row }">
            <span>{{ row.createTime || '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.operate')" fixed="right" width="240">
          <template #default="{ row }">
            <el-button link type="primary" @click="openEditDialog(row)">{{
              t('common.edit')
            }}</el-button>
            <el-button link type="primary" @click="handleTestConnection(row)">
              {{ t('auth_provider.test_connection') }}
            </el-button>
            <el-button link type="danger" @click="handleDelete(row)">{{
              t('common.delete')
            }}</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <auth-provider-edit ref="editRef" @saved="loadData" />
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus-secondary'
import { useI18n } from '@/hooks/web/useI18n'
import {
  authProviderList,
  authProviderDelete,
  authProviderToggle,
  authProviderSetDefault,
  authProviderTest
} from '@/api/auth-provider'
import type { AuthProvider } from '@/api/auth-provider'
import AuthProviderEdit from './AuthProviderEdit.vue'

const { t } = useI18n()
const loading = ref(false)
const providers = ref<AuthProvider[]>([])
const editRef = ref<InstanceType<typeof AuthProviderEdit>>()

const loadData = async () => {
  loading.value = true
  try {
    const res = await authProviderList()
    providers.value = res.data || []
  } finally {
    loading.value = false
  }
}

const handleToggle = async (row: AuthProvider) => {
  await authProviderToggle(row.id, { enabled: row.enabled })
  ElMessage.success(t('common.save_success'))
}

const handleSetDefault = async (row: AuthProvider) => {
  await authProviderSetDefault(row.id)
  ElMessage.success(t('common.save_success'))
  await loadData()
}

const handleTestConnection = async (row: AuthProvider) => {
  try {
    await authProviderTest(row.id, { credentials: {} })
    ElMessage.success(t('auth_provider.test_success'))
  } catch {
    ElMessage.error(t('auth_provider.test_failed'))
  }
}

const handleDelete = async (row: AuthProvider) => {
  await ElMessageBox.confirm(t('auth_provider.delete_confirm'), { type: 'warning' })
  await authProviderDelete(row.id)
  ElMessage.success(t('common.delete_success'))
  await loadData()
}

const openCreateDialog = () => editRef.value?.open('create')
const openEditDialog = (row: AuthProvider) => editRef.value?.open('edit', row)

onMounted(() => loadData())
</script>

<style lang="less" scoped>
.auth-provider-page {
  padding: 16px 24px;
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
  }
  .page-body {
    background: var(--ContentBG, #ffffff);
    border-radius: 4px;
    padding: 16px;
  }
}
</style>
