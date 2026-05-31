<script lang="ts" setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus-secondary'
import { useI18n } from '@/hooks/web/useI18n'
import type { FormInstance, FormRules } from 'element-plus-secondary'
import { filingConfigCreate, filingConfigUpdate } from '@/api/data-filing'
import { queryDatasources } from '@/api/datasource'
import type {
  FilingConfig,
  FilingConfigCreateRequest,
  FilingConfigUpdateRequest
} from '@/api/data-filing'

interface DatasourceOption {
  id: number
  name: string
}

const { t } = useI18n()
const emits = defineEmits(['saved'])
const drawerVisible = ref(false)
const mode = ref<'create' | 'edit'>('create')
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const defaultForm = (): FilingConfigCreateRequest => ({
  name: '',
  targetDatasourceId: null,
  targetTable: null,
  formSchema: {},
  fieldMapping: {},
  idempotencyWindowSeconds: 300
})

const form = ref<FilingConfigCreateRequest>(defaultForm())
const formSchemaText = ref('{}')
const fieldMappingText = ref('{}')
const datasourceLoading = ref(false)
const datasourceOptions = ref<DatasourceOption[]>([])

const formRules = ref<FormRules>({
  name: [{ required: true, message: t('common.please_input'), trigger: 'blur' }]
})

const open = (m: 'create' | 'edit', row?: FilingConfig) => {
  mode.value = m
  editingId.value = null
  if (m === 'edit' && row) {
    editingId.value = row.id
    form.value = {
      name: row.name,
      targetDatasourceId: row.targetDatasourceId,
      targetTable: row.targetTable,
      formSchema: row.formSchema,
      fieldMapping: row.fieldMapping,
      idempotencyWindowSeconds: row.idempotencyWindowSeconds
    }
    formSchemaText.value = JSON.stringify(row.formSchema || {}, null, 2)
    fieldMappingText.value = JSON.stringify(row.fieldMapping || {}, null, 2)
  } else {
    form.value = defaultForm()
    formSchemaText.value = '{}'
    fieldMappingText.value = '{}'
  }
  void loadDatasources()
  drawerVisible.value = true
}

const loadDatasources = async () => {
  datasourceLoading.value = true
  try {
    const res = await queryDatasources('_')
    datasourceOptions.value = (res.data || []).map(item => ({
      id: Number(item.id),
      name: item.name
    }))
  } finally {
    datasourceLoading.value = false
  }
}

const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate()
  try {
    form.value.formSchema = JSON.parse(formSchemaText.value)
    form.value.fieldMapping = JSON.parse(fieldMappingText.value)
  } catch {
    ElMessage.error('Invalid JSON in form schema or field mapping')
    return
  }
  if (mode.value === 'create') {
    await filingConfigCreate(form.value)
  } else if (editingId.value !== null) {
    const updateData: FilingConfigUpdateRequest = {
      name: form.value.name,
      targetDatasourceId: form.value.targetDatasourceId,
      targetTable: form.value.targetTable,
      formSchema: form.value.formSchema,
      fieldMapping: form.value.fieldMapping,
      idempotencyWindowSeconds: form.value.idempotencyWindowSeconds
    }
    await filingConfigUpdate(editingId.value, updateData)
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
    :title="mode === 'create' ? t('data_filing.create_config') : t('data_filing.edit_config')"
    v-model="drawerVisible"
    size="600px"
    direction="rtl"
  >
    <el-form ref="formRef" :model="form" :rules="formRules" label-position="top">
      <el-form-item :label="t('data_filing.config_name')" prop="name">
        <el-input v-model="form.name" :placeholder="t('common.please_input')" />
      </el-form-item>
      <el-form-item :label="t('data_filing.config_target')">
        <div style="display: flex; gap: 8px; width: 100%">
          <el-select
            v-model="form.targetDatasourceId"
            clearable
            filterable
            :loading="datasourceLoading"
            :placeholder="t('common.please_select')"
            style="flex: 1"
          >
            <el-option
              v-for="item in datasourceOptions"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
          <el-input v-model="form.targetTable" :placeholder="'Table name'" style="flex: 1" />
        </div>
      </el-form-item>
      <el-form-item :label="t('data_filing.config_form_schema')">
        <el-input v-model="formSchemaText" type="textarea" :rows="6" placeholder="JSON" />
      </el-form-item>
      <el-form-item :label="t('data_filing.config_field_mapping')">
        <el-input v-model="fieldMappingText" type="textarea" :rows="6" placeholder="JSON" />
      </el-form-item>
      <el-form-item :label="t('data_filing.config_idempotency')">
        <el-input-number v-model="form.idempotencyWindowSeconds" :min="0" :step="60" />
        <span style="margin-left: 8px">s</span>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="closeDrawer">{{ t('common.cancel') }}</el-button>
      <el-button type="primary" @click="submitForm">{{ t('common.sure') }}</el-button>
    </template>
  </el-drawer>
</template>
