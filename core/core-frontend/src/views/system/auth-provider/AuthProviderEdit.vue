<script lang="ts" setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus-secondary'
import { useI18n } from '@/hooks/web/useI18n'
import type { FormInstance, FormRules } from 'element-plus-secondary'
import { authProviderCreate, authProviderUpdate } from '@/api/auth-provider'
import type { AuthProvider, AuthProviderCreateRequest } from '@/api/auth-provider'

const { t } = useI18n()
const emits = defineEmits(['saved'])
const drawerVisible = ref(false)
const mode = ref<'create' | 'edit'>('create')
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const defaultForm = (): AuthProviderCreateRequest => ({
  name: '',
  type: 'ldap',
  config: null,
  claimMapping: null,
  enabled: true,
  isDefault: false
})

const form = reactive<AuthProviderCreateRequest>(defaultForm())

const formRules = reactive<FormRules>({
  name: [{ required: true, message: t('common.please_input'), trigger: 'blur' }],
  type: [{ required: true, message: t('common.please_select'), trigger: 'change' }]
})

const open = (m: 'create' | 'edit', row?: AuthProvider) => {
  mode.value = m
  Object.assign(form, defaultForm())
  editingId.value = null
  if (m === 'edit' && row) {
    editingId.value = row.id
    Object.assign(form, {
      name: row.name,
      type: row.type,
      config: row.config,
      claimMapping: row.claimMapping,
      enabled: row.enabled,
      isDefault: row.isDefault
    })
  }
  drawerVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  if (mode.value === 'create') {
    await authProviderCreate(form)
  } else if (editingId.value !== null) {
    await authProviderUpdate(editingId.value, form)
  }
  ElMessage.success(t('common.save_success'))
  drawerVisible.value = false
  emits('saved')
}

const closeDrawer = () => {
  formRef.value?.resetFields()
  drawerVisible.value = false
}

defineExpose({ open })
</script>

<template>
  <el-drawer
    :title="mode === 'create' ? t('auth_provider.create') : t('auth_provider.edit')"
    v-model="drawerVisible"
    size="600px"
    direction="rtl"
  >
    <el-form ref="formRef" :model="form" :rules="formRules" label-position="top">
      <el-form-item :label="t('auth_provider.name')" prop="name">
        <el-input v-model="form.name" :placeholder="t('common.please_input')" />
      </el-form-item>
      <el-form-item :label="t('auth_provider.type')" prop="type">
        <el-select v-model="form.type" :disabled="mode === 'edit'" style="width: 100%">
          <el-option label="LDAP" value="ldap" />
          <el-option label="OIDC" value="oidc" />
          <el-option label="CAS" value="cas" />
          <el-option label="Mock" value="mock" />
        </el-select>
      </el-form-item>
      <el-form-item :label="t('auth_provider.config')">
        <el-input
          v-model="form.config"
          type="textarea"
          :rows="6"
          placeholder='{"host": "", "port": 389, ...}'
        />
      </el-form-item>
      <el-form-item :label="t('auth_provider.claim_mapping')">
        <el-input
          v-model="form.claimMapping"
          type="textarea"
          :rows="3"
          placeholder='{"username": "uid", "email": "mail"}'
        />
      </el-form-item>
      <el-form-item :label="t('auth_provider.status')">
        <el-switch v-model="form.enabled" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="closeDrawer">{{ t('common.cancel') }}</el-button>
      <el-button type="primary" @click="submitForm">{{ t('common.sure') }}</el-button>
    </template>
  </el-drawer>
</template>
