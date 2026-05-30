<template>
  <div class="filing-audit-tab">
    <el-empty v-if="!filingId" :description="t('data_filing.tab_configs')" />
    <template v-else>
      <el-table :data="auditRecords" border v-loading="loading">
        <el-table-column :label="t('data_filing.audit_action')" width="140">
          <template #default="{ row }">
            <el-tag>{{ row.action }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="actorUid" :label="t('data_filing.audit_actor')" width="100" />
        <el-table-column :label="t('data_filing.audit_outcome')" width="100">
          <template #default="{ row }">
            <el-tag :type="row.outcome === 'success' ? 'success' : 'danger'">
              {{
                row.outcome === 'success'
                  ? t('data_filing.outcome_success')
                  : t('data_filing.outcome_failure')
              }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="details"
          :label="t('data_filing.audit_details')"
          min-width="200"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <span>{{ row.details ? JSON.stringify(row.details) : '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="errorCode" label="Error" width="120" show-overflow-tooltip />
        <el-table-column prop="createTime" :label="t('data_filing.audit_time')" min-width="160" />
      </el-table>
    </template>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch } from 'vue'
import { useI18n } from '@/hooks/web/useI18n'
import { filingAuditList } from '@/api/data-filing'
import type { FilingAudit } from '@/api/data-filing'

const props = defineProps<{ filingId: number }>()
const { t } = useI18n()
const loading = ref(false)
const auditRecords = ref<FilingAudit[]>([])

const loadData = async () => {
  if (!props.filingId) return
  loading.value = true
  try {
    const res = await filingAuditList(props.filingId)
    auditRecords.value = res.data || []
  } finally {
    loading.value = false
  }
}

watch(() => props.filingId, loadData, { immediate: true })
</script>
