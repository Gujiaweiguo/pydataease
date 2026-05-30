<template>
  <div class="feature-flag-page" v-loading="loading">
    <div v-for="item in flagItems" :key="item.key" class="feature-item">
      <span class="feature-label">{{ item.label }}</span>
      <el-switch v-model="flags[item.key]" @change="() => handleToggle(item.key)" />
    </div>
  </div>
</template>

<script lang="ts" setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus-secondary'
import { useI18n } from '@/hooks/web/useI18n'
import { featureStatus, featureToggle } from '@/api/feature-flag'
import { useFeatureFlagStoreWithOut, FEATURE_KEYS } from '@/store/modules/feature-flag'
import type { FeatureKey } from '@/store/modules/feature-flag'

const { t } = useI18n()
const featureFlagStore = useFeatureFlagStoreWithOut()
const loading = ref(false)

const flagItems: { key: FeatureKey; label: string }[] = [
  { key: FEATURE_KEYS.adminConfig, label: t('feature_flag.admin_config') },
  { key: FEATURE_KEYS.appearance, label: t('feature_flag.appearance') },
  { key: FEATURE_KEYS.watermark, label: t('feature_flag.watermark') },
  { key: FEATURE_KEYS.sysVariable, label: t('feature_flag.sys_variable_contract') },
  { key: FEATURE_KEYS.embedding, label: t('feature_flag.embedding') },
  { key: FEATURE_KEYS.platformIntegration, label: t('feature_flag.platform_integration') },
  { key: FEATURE_KEYS.identification, label: t('feature_flag.identification') },
  { key: FEATURE_KEYS.dataFiling, label: t('feature_flag.data_filing') }
]

const flags = reactive<Record<string, boolean>>(
  Object.fromEntries(flagItems.map(item => [item.key, false]))
)

const loadData = async () => {
  loading.value = true
  try {
    const res = await featureStatus()
    const data: Record<string, boolean> = res.data || {}
    for (const key of Object.keys(flags)) {
      if (key in data) {
        flags[key] = data[key]
      }
    }
  } finally {
    loading.value = false
  }
}

const handleToggle = async (key: string) => {
  await featureToggle({ key, enabled: flags[key] })
  featureFlagStore.setFlag(key as FeatureKey, flags[key])
  ElMessage.success(t('feature_flag.toggle_success'))
}

onMounted(() => loadData())
</script>

<style lang="less" scoped>
.feature-flag-page {
  padding: 16px;
  .feature-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid var(--ed-border-color-lighter, #ebeef5);
    &:last-child {
      border-bottom: none;
    }
  }
  .feature-label {
    font-size: 14px;
    color: var(--ed-text-color-primary, #1f2329);
  }
}
</style>
