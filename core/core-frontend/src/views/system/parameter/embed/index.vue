<template>
  <div class="embed-control-page" v-loading="loading">
    <el-card v-for="rt in resourceTypes" :key="rt" class="embed-card" shadow="never">
      <div class="embed-card-header">
        <span class="embed-card-title">{{ t(`embed_control.resource_${rt}`) }}</span>
        <el-switch v-model="configMap[rt].embedEnabled" @change="() => handleToggle(rt)" />
      </div>
      <div class="embed-card-body">
        <div class="info-row">
          <span class="info-label">{{ t('embed_control.allowed_domains') }}:</span>
          <span class="info-value">{{ formatDomains(configMap[rt].allowedDomains) }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">{{ t('embed_control.password_required') }}:</span>
          <span class="info-value">{{
            configMap[rt].passwordRequired ? t('common.sure') : t('common.cancel')
          }}</span>
        </div>
        <div class="info-row">
          <span class="info-label">{{ t('embed_control.max_expiry_hours') }}:</span>
          <span class="info-value">{{
            configMap[rt].maxExpiryHours || t('embed_control.max_expiry_unlimited')
          }}</span>
        </div>
        <el-button type="primary" link @click="openEdit(rt)">{{ t('common.edit') }}</el-button>
      </div>
    </el-card>
    <embed-edit ref="editRef" @saved="loadData" />
  </div>
</template>

<script lang="ts" setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus-secondary'
import { useI18n } from '@/hooks/web/useI18n'
import { embedControlList, embedControlUpdate } from '@/api/embed-control'
import type { EmbedConfig } from '@/api/embed-control'
import EmbedEdit from './EmbedEdit.vue'

const { t } = useI18n()
const loading = ref(false)
const editRef = ref<InstanceType<typeof EmbedEdit>>()

const resourceTypes = ['dashboard', 'chart', 'datav', 'dataFiling'] as const

const defaultConfig = (): EmbedConfig => ({
  id: 0,
  resourceType: 'dashboard',
  embedEnabled: false,
  allowedDomains: [],
  passwordRequired: false,
  ticketRequired: false,
  maxExpiryHours: null,
  extraConfig: null,
  createTime: null,
  updateTime: null
})

const configMap = reactive<Record<string, EmbedConfig>>(
  Object.fromEntries(resourceTypes.map(rt => [rt, defaultConfig()]))
)

const loadData = async () => {
  loading.value = true
  try {
    const res = await embedControlList()
    const list: EmbedConfig[] = res.data || []
    for (const cfg of list) {
      if (configMap[cfg.resourceType]) {
        Object.assign(configMap[cfg.resourceType], cfg)
      }
    }
  } finally {
    loading.value = false
  }
}

const handleToggle = async (rt: string) => {
  await embedControlUpdate(rt, { embedEnabled: configMap[rt].embedEnabled })
  ElMessage.success(t('common.save_success'))
}

const openEdit = (rt: string) => editRef.value?.open(rt, configMap[rt])

const formatDomains = (domains?: string[] | null) => {
  if (!domains || domains.length === 0) return t('embed_control.allowed_domains_placeholder')
  return domains.join(', ')
}

onMounted(() => loadData())
</script>

<style lang="less" scoped>
.embed-control-page {
  padding: 16px;
  .embed-card {
    margin-bottom: 16px;
    border-radius: 8px;
  }
  .embed-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }
  .embed-card-title {
    font-weight: 500;
    font-size: 15px;
  }
  .embed-card-body {
    .info-row {
      display: flex;
      margin-bottom: 8px;
      font-size: 13px;
    }
    .info-label {
      color: var(--ed-text-color-secondary, #8f959e);
      width: 120px;
      flex-shrink: 0;
    }
    .info-value {
      color: var(--ed-text-color-primary, #1f2329);
    }
  }
}
</style>
