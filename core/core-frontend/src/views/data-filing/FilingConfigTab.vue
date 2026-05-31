<template>
  <div class="filing-config-tab">
    <div class="toolbar" style="margin-bottom: 12px">
      <el-button type="primary" @click="openCreateDialog">{{
        t('data_filing.create_config')
      }}</el-button>
      <el-select
        v-model="statusFilter"
        clearable
        :placeholder="t('data_filing.config_status')"
        style="width: 140px; margin-left: 12px"
        @change="loadData"
      >
        <el-option :label="t('data_filing.status_draft')" value="draft" />
        <el-option :label="t('data_filing.status_published')" value="published" />
        <el-option :label="t('data_filing.status_disabled')" value="disabled" />
      </el-select>
    </div>

    <el-table :data="configs" border v-loading="loading">
      <el-table-column prop="name" :label="t('data_filing.config_name')" min-width="160" />
      <el-table-column :label="t('data_filing.config_status')" width="120">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('data_filing.config_target')" min-width="180">
        <template #default="{ row }">
          <span>{{ row.targetDatasourceId || '-' }} / {{ row.targetTable || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('data_filing.config_idempotency')" width="140">
        <template #default="{ row }">
          <span>{{ row.idempotencyWindowSeconds }}s</span>
        </template>
      </el-table-column>
      <el-table-column :label="t('common.operate')" fixed="right" width="240">
        <template #default="{ row }">
          <el-button v-if="row.status === 'draft'" link type="primary" @click="openEditDialog(row)">
            {{ t('common.edit') }}
          </el-button>
          <el-button v-if="row.status === 'draft'" link type="success" @click="handlePublish(row)">
            {{ t('data_filing.publish') }}
          </el-button>
          <el-button v-if="row.status === 'draft'" link type="danger" @click="handleDelete(row)">
            {{ t('common.delete') }}
          </el-button>
          <el-button
            v-if="row.status === 'published'"
            link
            type="warning"
            @click="handleDisable(row)"
          >
            {{ t('data_filing.disable') }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <filing-config-edit ref="editRef" @saved="loadData" />
  </div>
</template>

<script lang="ts" setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus-secondary'
import { useI18n } from '@/hooks/web/useI18n'
import {
  filingConfigDelete,
  filingConfigDisable,
  filingConfigList,
  filingConfigPublish
} from '@/api/data-filing'
import type { FilingConfig, FilingConfigStatus } from '@/api/data-filing'
import FilingConfigEdit from './FilingConfigEdit.vue'

const { t } = useI18n()
const emits = defineEmits(['select'])
const loading = ref(false)
const configs = ref<FilingConfig[]>([])
const statusFilter = ref<string>('')
const editRef = ref<InstanceType<typeof FilingConfigEdit>>()

const loadData = async () => {
  loading.value = true
  try {
    const res = await filingConfigList(statusFilter.value || undefined)
    configs.value = res.data || []
  } finally {
    loading.value = false
  }
}

const statusTagType = (status: FilingConfigStatus) => {
  const map: Record<string, string> = { draft: 'info', published: 'success', disabled: 'danger' }
  return map[status] || 'info'
}

const statusLabel = (status: FilingConfigStatus) => {
  const map: Record<string, string> = {
    draft: t('data_filing.status_draft'),
    published: t('data_filing.status_published'),
    disabled: t('data_filing.status_disabled')
  }
  return map[status] || status
}

const handlePublish = async (row: FilingConfig) => {
  await ElMessageBox.confirm(t('data_filing.publish_confirm'), { type: 'warning' })
  await filingConfigPublish(row.id)
  ElMessage.success(t('data_filing.publish_success'))
  await loadData()
  emits('select', row.id)
}

const handleDisable = async (row: FilingConfig) => {
  await ElMessageBox.confirm(t('data_filing.disable_confirm'), { type: 'warning' })
  await filingConfigDisable(row.id)
  ElMessage.success(t('data_filing.disable_success'))
  await loadData()
}

const handleDelete = async (row: FilingConfig) => {
  await ElMessageBox.confirm(t('common.delete_confirm'), { type: 'warning' })
  await filingConfigDelete(row.id)
  ElMessage.success(t('common.delete_success'))
  await loadData()
}

const openCreateDialog = () => editRef.value?.open('create')
const openEditDialog = (row: FilingConfig) => editRef.value?.open('edit', row)

onMounted(() => loadData())
</script>
