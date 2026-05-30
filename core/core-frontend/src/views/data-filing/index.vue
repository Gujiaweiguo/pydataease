<template>
  <div class="data-filing-page">
    <el-tabs v-model="activeTab">
      <el-tab-pane :label="t('data_filing.tab_configs')" name="configs">
        <filing-config-tab @select="handleSelectConfig" />
      </el-tab-pane>
      <el-tab-pane :label="t('data_filing.tab_submissions')" name="submissions">
        <filing-submission-tab :filing-id="selectedFilingId" />
      </el-tab-pane>
      <el-tab-pane :label="t('data_filing.tab_audit')" name="audit">
        <filing-audit-tab :filing-id="selectedFilingId" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue'
import { useI18n } from '@/hooks/web/useI18n'
import FilingConfigTab from './FilingConfigTab.vue'
import FilingSubmissionTab from './FilingSubmissionTab.vue'
import FilingAuditTab from './FilingAuditTab.vue'

const { t } = useI18n()
const activeTab = ref('configs')
const selectedFilingId = ref(0)

const handleSelectConfig = (id: number) => {
  selectedFilingId.value = id
}
</script>

<style lang="less" scoped>
.data-filing-page {
  padding: 16px 24px;
}
</style>
