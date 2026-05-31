<script lang="ts" setup>
import { ref, watch } from 'vue'
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
import FormBuilder from './FormBuilder.vue'
import FormPreview from './FormPreview.vue'

interface FormSchemaField {
  fieldKey?: string
}

interface FormSchemaModel {
  fields: FormSchemaField[]
}

interface DatasourceOption {
  id: number
  name: string
}

const { t } = useI18n()
const emits = defineEmits(['saved'])
const drawerVisible = ref(false)
const previewVisible = ref(false)
const mode = ref<'create' | 'edit'>('create')
const editingId = ref<number | null>(null)
const formRef = ref<FormInstance>()

const defaultForm = (): FilingConfigCreateRequest => ({
  name: '',
  targetDatasourceId: null,
  targetTable: null,
  formSchema: { fields: [] },
  fieldMapping: {},
  idempotencyWindowSeconds: 300
})

const form = ref<FilingConfigCreateRequest>(defaultForm())
const fieldMappingText = ref('{}')
const fieldMappingDraft = ref<Record<string, string>>({})
const datasourceLoading = ref(false)
const datasourceOptions = ref<DatasourceOption[]>([])

const formRules = ref<FormRules>({
  name: [{ required: true, message: t('common.please_input'), trigger: 'blur' }]
})

const normalizeFormSchema = (schema?: Record<string, unknown> | null): FormSchemaModel => {
  return {
    fields: Array.isArray(schema?.fields) ? (schema.fields as FormSchemaField[]) : []
  }
}

const buildFieldMapping = (
  schema: Record<string, unknown> | null | undefined,
  source: Record<string, string>
) => {
  const nextMapping: Record<string, string> = {}
  normalizeFormSchema(schema).fields.forEach(field => {
    const fieldKey = typeof field.fieldKey === 'string' ? field.fieldKey.trim() : ''
    if (!fieldKey) {
      return
    }
    nextMapping[fieldKey] = source[fieldKey]?.trim() || fieldKey
  })
  return nextMapping
}

const syncFieldMappingText = () => {
  fieldMappingText.value = JSON.stringify(fieldMappingDraft.value, null, 2)
}

const open = (m: 'create' | 'edit', row?: FilingConfig) => {
  mode.value = m
  editingId.value = null
  if (m === 'edit' && row) {
    editingId.value = row.id
    form.value = {
      name: row.name,
      targetDatasourceId: row.targetDatasourceId,
      targetTable: row.targetTable,
      formSchema: normalizeFormSchema(row.formSchema),
      fieldMapping: row.fieldMapping,
      idempotencyWindowSeconds: row.idempotencyWindowSeconds
    }
    fieldMappingDraft.value = buildFieldMapping(
      row.formSchema,
      (row.fieldMapping || {}) as Record<string, string>
    )
    syncFieldMappingText()
  } else {
    form.value = defaultForm()
    fieldMappingDraft.value = buildFieldMapping(form.value.formSchema, {})
    syncFieldMappingText()
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
    form.value.fieldMapping = JSON.parse(fieldMappingText.value)
  } catch {
    ElMessage.error(t('data_filing.form_builder.invalid_field_mapping'))
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
  previewVisible.value = false
  drawerVisible.value = false
}

watch(
  () => form.value.formSchema,
  schema => {
    fieldMappingDraft.value = buildFieldMapping(schema, fieldMappingDraft.value)
    syncFieldMappingText()
  },
  { deep: true }
)

watch(fieldMappingText, value => {
  try {
    const parsed = JSON.parse(value)
    if (parsed && typeof parsed === 'object' && !Array.isArray(parsed)) {
      fieldMappingDraft.value = parsed as Record<string, string>
    }
  } catch {
    return
  }
})

defineExpose({ open })
</script>

<template>
  <el-drawer
    :title="mode === 'create' ? t('data_filing.create_config') : t('data_filing.edit_config')"
    v-model="drawerVisible"
    size="1000px"
    direction="rtl"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="formRules"
      class="filing-config-form"
      label-position="top"
    >
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
        <div class="schema-toolbar">
          <span class="schema-toolbar__title">{{ t('data_filing.form_builder.title') }}</span>
          <el-button link type="primary" @click="previewVisible = true">
            {{ t('data_filing.form_builder.preview') }}
          </el-button>
        </div>
        <FormBuilder v-model="form.formSchema" />
      </el-form-item>
      <el-form-item :label="t('data_filing.config_field_mapping')">
        <el-input
          v-model="fieldMappingText"
          class="field-mapping-textarea"
          type="textarea"
          :rows="6"
          placeholder="JSON"
        />
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
  <FormPreview v-model="previewVisible" :schema="form.formSchema" />
</template>

<style lang="less" scoped>
.filing-config-form {
  --filing-space-1: 4px;
  --filing-space-2: 8px;
  --filing-space-3: 12px;
  --filing-space-4: 16px;
  --filing-space-5: 20px;
  font-family: var(--de-custom_font, 'PingFang');
}

.schema-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--filing-space-3);
}

.schema-toolbar__title {
  color: var(--ed-text-color-primary, #1f2329);
  font-size: 14px;
  font-weight: 500;
  line-height: 22px;
}

.field-mapping-textarea {
  :deep(.ed-textarea__inner) {
    min-height: 144px;
    font-family: Monaco, Consolas, 'Courier New', monospace;
  }
}
</style>
