<template>
  <div class="filing-submission-tab">
    <el-empty v-if="!filingId" :description="t('data_filing.tab_configs')" />
    <template v-else>
      <el-table :data="submissions" border v-loading="loading">
        <el-table-column prop="id" label="ID" width="100" />
        <el-table-column :label="t('data_filing.submission_status')" width="120">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="payloadHash" label="Hash" min-width="140" show-overflow-tooltip />
        <el-table-column
          prop="errorMessage"
          :label="t('common.description')"
          min-width="180"
          show-overflow-tooltip
        />
        <el-table-column :label="t('data_filing.retry')" width="80">
          <template #default="{ row }">
            <span>{{ row.retryCount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="submitterUid" :label="t('data_filing.audit_actor')" width="100" />
        <el-table-column prop="createTime" :label="t('common.create_time')" min-width="160" />
        <el-table-column :label="t('common.operate')" fixed="right" width="100">
          <template #default="{ row }">
            <el-button v-if="row.status === 'failed'" link type="primary" @click="handleRetry(row)">
              {{ t('data_filing.retry') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </template>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus-secondary'
import { useI18n } from '@/hooks/web/useI18n'
import { filingSubmissions, filingSubmissionRetry } from '@/api/data-filing'
import type { FilingSubmission, SubmissionStatus } from '@/api/data-filing'

const props = defineProps<{ filingId: number }>()
const { t } = useI18n()
const loading = ref(false)
const submissions = ref<FilingSubmission[]>([])

const loadData = async () => {
  if (!props.filingId) return
  loading.value = true
  try {
    const res = await filingSubmissions(props.filingId)
    submissions.value = res.data || []
  } finally {
    loading.value = false
  }
}

const statusTagType = (status: SubmissionStatus) => {
  const map: Record<string, string> = {
    pending: 'warning',
    success: 'success',
    failed: 'danger',
    retrying: 'warning'
  }
  return map[status] || 'info'
}

const statusLabel = (status: SubmissionStatus) => {
  const map: Record<string, string> = {
    pending: t('data_filing.submission_pending'),
    success: t('data_filing.submission_success'),
    failed: t('data_filing.submission_failed'),
    retrying: t('data_filing.submission_retrying')
  }
  return map[status] || status
}

const handleRetry = async (row: FilingSubmission) => {
  await filingSubmissionRetry(row.id)
  ElMessage.success(t('data_filing.retry_success'))
  await loadData()
}

watch(() => props.filingId, loadData, { immediate: true })
</script>
