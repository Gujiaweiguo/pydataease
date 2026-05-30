<script lang="ts" setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus-secondary'
import { useI18n } from '@/hooks/web/useI18n'
import { embedControlGet, embedControlUpdate } from '@/api/embed-control'
import type { EmbedConfig, EmbedConfigUpdateRequest } from '@/api/embed-control'

const { t } = useI18n()
const emits = defineEmits(['saved'])
const drawerVisible = ref(false)
const resourceType = ref('')

const form = ref<EmbedConfigUpdateRequest>({
  embedEnabled: false,
  allowedDomains: [],
  passwordRequired: false,
  ticketRequired: false,
  maxExpiryHours: null,
  extraConfig: null
})

const domainsText = ref('')

const open = async (rt: string, current: EmbedConfig) => {
  resourceType.value = rt
  try {
    const res = await embedControlGet(rt)
    const cfg = res.data
    if (cfg) {
      form.value = {
        embedEnabled: cfg.embedEnabled,
        allowedDomains: cfg.allowedDomains,
        passwordRequired: cfg.passwordRequired,
        ticketRequired: cfg.ticketRequired,
        maxExpiryHours: cfg.maxExpiryHours,
        extraConfig: cfg.extraConfig
      }
      domainsText.value = (cfg.allowedDomains || []).join('\n')
    }
  } catch {
    form.value = {
      embedEnabled: current.embedEnabled,
      allowedDomains: [],
      passwordRequired: false,
      ticketRequired: false,
      maxExpiryHours: null,
      extraConfig: null
    }
    domainsText.value = ''
  }
  drawerVisible.value = true
}

const submitForm = async () => {
  const domains = domainsText.value
    .split('\n')
    .map(d => d.trim())
    .filter(d => d.length > 0)
  const data: EmbedConfigUpdateRequest = {
    ...form.value,
    allowedDomains: domains
  }
  await embedControlUpdate(resourceType.value, data)
  ElMessage.success(t('common.save_success'))
  drawerVisible.value = false
  emits('saved')
}

const closeDrawer = () => {
  drawerVisible.value = false
}

defineExpose({ open })
</script>

<template>
  <el-drawer :title="t('embed_control.title')" v-model="drawerVisible" size="600px" direction="rtl">
    <el-form :model="form" label-position="top">
      <el-form-item :label="t('embed_control.embed_enabled')">
        <el-switch v-model="form.embedEnabled" />
      </el-form-item>
      <el-form-item :label="t('embed_control.allowed_domains')">
        <el-input
          v-model="domainsText"
          type="textarea"
          :rows="4"
          :placeholder="t('embed_control.allowed_domains_placeholder')"
        />
      </el-form-item>
      <el-form-item :label="t('embed_control.password_required')">
        <el-switch v-model="form.passwordRequired" />
      </el-form-item>
      <el-form-item :label="t('embed_control.ticket_required')">
        <el-switch v-model="form.ticketRequired" />
      </el-form-item>
      <el-form-item :label="t('embed_control.max_expiry_hours')">
        <el-input-number v-model="form.maxExpiryHours" :min="0" :step="1" />
        <span style="margin-left: 8px; color: var(--ed-text-color-secondary)">
          {{ t('embed_control.max_expiry_unlimited') }}
        </span>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="closeDrawer">{{ t('common.cancel') }}</el-button>
      <el-button type="primary" @click="submitForm">{{ t('common.sure') }}</el-button>
    </template>
  </el-drawer>
</template>
